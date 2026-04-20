"""
SciGrader 作业管理 API 路由
提供作业的增删改查、提交等功能
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import database manager from backend (not frontend!)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.db_manager import get_db_manager
    logger.info("✅ Successfully imported DatabaseManager from backend.db_manager")
except ImportError as e:
    logger.warning(f"❌ Could not import db_manager from backend: {e}")
    logger.warning("⚠️ Using mock implementation - NO DATABASE PERSISTENCE!")
    
    class MockDatabaseManager:
        """Mock database manager for when real DB is not available"""
        def create_connection(self):
            return False
        def execute_query(self, query, params=None, fetch=False):
            logger.warning(f"Mock DB call: {query[:50]}...")
            return [] if fetch else True
    
    def get_db_manager():
        return MockDatabaseManager()

router = APIRouter(prefix="/api/assignments", tags=["assignments"])


class AssignmentCreate(BaseModel):
    hw_code: str
    teacher_id: int
    title: str
    description: str
    course_name: str
    total_score: float
    due_time: datetime
    questions: List[Dict[str, Any]] = []


class AssignmentResponse(BaseModel):
    hw_id: int
    hw_code: str
    title: str
    description: Optional[str]
    course_name: Optional[str]
    total_score: float
    due_time: datetime
    assignment_status: str
    submit_status: str
    submit_id: Optional[int]
    submitted_score: Optional[float]
    submit_time: Optional[datetime]
    attempt_no: Optional[int]


class SubmissionCreate(BaseModel):
    hw_id: int
    student_id: int
    answers: Dict[str, Any]


@router.post("/create", summary="创建作业")
async def create_assignment(assignment: AssignmentCreate):
    db = get_db_manager()
    try:
        # 1. 创建作业
        hw_id = db.create_assignment(
            hw_code=assignment.hw_code,
            teacher_id=assignment.teacher_id,
            title=assignment.title,
            description=assignment.description,
            course_name=assignment.course_name,
            total_score=assignment.total_score,
            due_time=assignment.due_time
        )
        
        # 2. 添加作业题目
        for idx, question in enumerate(assignment.questions):
            db.add_assignment_question(
                hw_id=hw_id,
                q_id=question['q_id'],
                question_order=idx + 1,
                score=question.get('score', 0)
            )
        
        logger.info(f"作业创建成功：hw_id={hw_id}")
        return {
            "status": "success",
            "message": "作业创建成功",
            "hw_id": hw_id
        }
        
    except Exception as e:
        logger.error(f"创建作业失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{student_id}", response_model=List[AssignmentResponse])
async def get_student_assignments(student_id: int):
    db = get_db_manager()
    try:
        assignments = db.get_assignments_for_student(student_id)
        
        result = []
        for a in assignments:
            result.append({
                "hw_id": a["hw_id"],
                "hw_code": a["hw_code"],
                "title": a["title"],
                "description": a["description"],
                "course_name": a["course_name"],
                "total_score": float(a["total_score"]),
                "due_time": a["due_time"],
                "assignment_status": a["assignment_status"],
                "submit_status": a["submit_status"],
                "submit_id": a["submit_id"],
                "submitted_score": float(a["submitted_score"]) if a["submitted_score"] else None,
                "submit_time": a["submit_time"],
                "attempt_no": a["attempt_no"]
            })
        
        logger.info(f"获取学生 {student_id} 的作业列表成功")
        return result
        
    except Exception as e:
        logger.error(f"获取作业列表失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{hw_id}/questions")
async def get_assignment_questions(hw_id: int):
    db = get_db_manager()
    try:
        questions = db.get_assignment_questions(hw_id)
        logger.info(f"获取作业 {hw_id} 的题目成功")
        return {
            "status": "success",
            "hw_id": hw_id,
            "questions": questions,
            "count": len(questions)
        }
        
    except Exception as e:
        logger.error(f"获取作业题目失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit")
async def submit_assignment(submission: SubmissionCreate):
    db = get_db_manager()
    try:
        existing = db.get_submission_by_student_and_hw(
            submission.student_id, 
            submission.hw_id
        )
        
        attempt_no = 1
        if existing:
            attempt_no = existing.get("attempt_no", 0) + 1
        
        submit_id = db.create_submission(
            hw_id=submission.hw_id,
            student_id=submission.student_id,
            submit_content=submission.answers,
            attempt_no=attempt_no
        )
        
        logger.info(f"作业提交成功：submit_id={submit_id}")
        return {
            "status": "success",
            "message": "作业提交成功",
            "submit_id": submit_id,
            "attempt_no": attempt_no
        }
        
    except Exception as e:
        logger.error(f"提交作业失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{student_id}")
async def get_student_stats(student_id: int):
    db = get_db_manager()
    try:
        assignments = db.get_assignments_for_student(student_id)
        
        total = len(assignments)
        completed = sum(1 for a in assignments if a.get("submit_status") == "submitted")
        pending = sum(1 for a in assignments if a.get("submit_status") == "pending")
        overdue = sum(1 for a in assignments if a.get("submit_status") == "overdue")
        
        completion_rate = round((completed / total * 100), 2) if total > 0 else 0
        
        stats = {
            "total_assignments": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "completion_rate": completion_rate
        }
        
        logger.info(f"获取学生 {student_id} 的统计数据成功")
        return {
            "status": "success",
            "student_id": student_id,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"获取统计数据失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{assignment_id}", summary="删除作业")
async def delete_assignment(assignment_id: int, teacher_id: int):
    """删除作业（只能删除自己创建的作业）
    
    Args:
        assignment_id: 作业ID
        teacher_id: 教师ID（用于验证权限）
        
    Returns:
        dict: 删除结果
    """
    db = get_db_manager()
    try:
        result = db.delete_assignment(assignment_id, teacher_id)
        
        if result:
            logger.info(f"作业删除成功：assignment_id={assignment_id}, teacher_id={teacher_id}")
            return {
                "status": "success",
                "message": "作业删除成功",
                "assignment_id": assignment_id
            }
        else:
            logger.warning(f"作业删除失败：assignment_id={assignment_id}, teacher_id={teacher_id}")
            raise HTTPException(
                status_code=404, 
                detail="作业不存在或无权删除"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除作业失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))
