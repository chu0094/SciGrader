// 交互动效和动画脚本 - Interactive Effects & Animations
//这个文件包含所有前端交互动效和动画逻辑

//等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有动画效果
    initAnimations();
    initInteractiveEffects();
    initParticleBackground();
});

// 初始化基础动画
function initAnimations() {
    //元进入视图时的动画
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    //观察所有需要动画的元素
    document.querySelectorAll('.card, .feature-card, .stats-card, .glass-card').forEach(el => {
        observer.observe(el);
    });
}

// 初始化交互动效
function initInteractiveEffects() {
    //按悬停效果增强
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.classList.add('button-hover');
        });
        
        button.addEventListener('mouseleave', function() {
            this.classList.remove('button-hover');
        });
        
        button.addEventListener('click', function() {
            this.classList.add('button-click');
            setTimeout(() => {
                this.classList.remove('button-click');
            }, 300);
        });
    });
    
    //卡悬停3D效果
    const cards = document.querySelectorAll('.card, .feature-card, .glass-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', handleCardMouseMove);
        card.addEventListener('mouseleave', handleCardMouseLeave);
    });
    
    // 输入框焦点效果
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
        });
    });
}

//卡鼠标移动处理
function handleCardMouseMove(e) {
    const card = this;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = (y - centerY) / 10;
    const rotateY = (centerX - x) / 10;
    
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
}

//卡鼠标离开处理
function handleCardMouseLeave() {
    this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
}

// 初始化粒子背景效果
function initParticleBackground() {
    // 创建canvas元素
    const canvas = document.createElement('canvas');
    canvas.id = 'particle-canvas';
    canvas.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
    `;
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    const particleCount = 50;
    
    // 设置canvas尺寸
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    
    // 创建粒子类
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.size = Math.random() * 2 + 1;
            this.opacity = Math.random() * 0.5 + 0.1;
            this.color = Math.random() > 0.5 ? '#00D4FF' : '#8B5CF6';
        }
        
        update() {
            this.x += this.vx;
            this.y += this.vy;
            
            //边界检测
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            
            //透明度波动
            this.opacity += (Math.random() - 0.5) * 0.02;
            this.opacity = Math.max(0.1, Math.min(0.6, this.opacity));
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.opacity;
            ctx.fill();
            ctx.globalAlpha = 1;
            
            // 添加光晕效果
            const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size * 3);
            gradient.addColorStop(0, this.color);
            gradient.addColorStop(1, 'transparent');
            
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
            ctx.fillStyle = gradient;
            ctx.globalAlpha = this.opacity * 0.3;
            ctx.fill();
            ctx.globalAlpha = 1;
        }
    }
    
    // 初始化粒子
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    //动画循环
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

// 添加CSS动画类
const additionalCSS = `
/*按钮悬停效果 */
.button-hover {
    transform: translateY(-2px) !important;
    transition: transform 0.2s ease !important;
}

/*按钮点击效果 */
.button-click {
    transform: scale(0.95) !important;
    transition: transform 0.1s ease !important;
}

/* 输入框焦点效果 */
.input-focused {
    box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.3) !important;
    border-color: #00D4FF !important;
}

/* 3D卡片效果 */
.card, .feature-card, .glass-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    transform-style: preserve-3d !important;
}

/*滚进度条 */
.scroll-progress {
    position: fixed;
    top: 0;
    left: 0;
    width: 0%;
    height: 3px;
    background: linear-gradient(90deg, #00D4FF, #8B5CF6, #00F5D4);
    z-index: 9999;
    transition: width 0.1s ease;
}

/* 加载指示器 */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(15, 23, 42, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    backdrop-filter: blur(10px);
}

.loading-spinner {
    width: 60px;
    height: 60px;
    border: 4px solid rgba(0, 212, 255, 0.3);
    border-top: 4px solid #00D4FF;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    position: relative;
}

.loading-spinner::before {
    content: '';
    position: absolute;
    top: -10px;
    left: -10px;
    right: -10px;
    bottom: -10px;
    border: 2px solid rgba(139, 92, 246, 0.2);
    border-radius: 50%;
    animation: spin 2s linear infinite reverse;
}

/*滚到顶部按钮 */
.scroll-to-top {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #00D4FF, #8B5CF6);
    border: none;
    border-radius: 50%;
    color: white;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
    transition: all 0.3s ease;
    z-index: 1000;
}

.scroll-to-top:hover {
    transform: translateY(-5px) scale(1.1);
    box-shadow: 0 10px 25px rgba(0, 212, 255, 0.6);
}

/*工具提示 */
.tooltip {
    position: relative;
    display: inline-block;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 200px;
    background: rgba(15, 23, 42, 0.95);
    color: #F1F5F9;
    text-align: center;
    border-radius: 8px;
    padding: 10px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(0, 212, 255, 0.3);
    font-size: 14px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}

.tooltip .tooltiptext::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: rgba(15, 23, 42, 0.95) transparent transparent transparent;
}
`;

//将CSS添加到页面
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalCSS;
document.head.appendChild(styleSheet);

// 添加滚动进度条
function addScrollProgress() {
    const progress = document.createElement('div');
    progress.className = 'scroll-progress';
    document.body.appendChild(progress);
    
    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset;
        const docHeight = document.body.offsetHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        progress.style.width = scrollPercent + '%';
    });
}

// 添加滚动到顶部按钮
function addScrollToTop() {
    const scrollTopBtn = document.createElement('button');
    scrollTopBtn.className = 'scroll-to-top';
    scrollTopBtn.innerHTML = '↑';
    scrollTopBtn.title = 'Scroll to top';
    document.body.appendChild(scrollTopBtn);
    
    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    //时显示/隐藏按钮
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollTopBtn.style.opacity = '1';
            scrollTopBtn.style.transform = 'scale(1)';
        } else {
            scrollTopBtn.style.opacity = '0';
            scrollTopBtn.style.transform = 'scale(0.8)';
        }
    });
}

// 页面加载完成后初始化额外功能
window.addEventListener('load', () => {
    addScrollProgress();
    addScrollToTop();
});

//导出函数供其他脚本使用
window.SmarTAIAnimations = {
    initAnimations,
    initInteractiveEffects,
    initParticleBackground
};