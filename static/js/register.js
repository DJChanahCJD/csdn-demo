$(document).ready(function() {
    // 初始化验证码按钮
    initializeCaptchaButton();
    // 初始化消息自动消失功能
    initializeMessages();
});

const countdownTime = 30;

// 初始化验证码按钮
function initializeCaptchaButton() {
    // 检查是否有剩余倒计时
    const remainingTime = localStorage.getItem('captchaCooldown');
    if (remainingTime && new Date().getTime() < remainingTime) {
        const timeLeft = Math.ceil((remainingTime - new Date().getTime()) / 1000);
        console.log('Found remaining cooldown time:', timeLeft);
        startCountdown(timeLeft);
    }
    
    // 绑定点击事件
    $('#get-captcha-btn').click(function() {
        sendCaptcha();
    });
}

// 发送验证码
function sendCaptcha() {
    // 获取邮箱输入框的值
    const email = $('#email').val();
    // console.log('Email value:', email);
    
    // 简单验证邮箱是否为空
    if (!email) {
        alert('请输入邮箱地址');
        return;
    }
    
    // 禁用按钮并显示加载状态
    $('#get-captcha-btn').prop('disabled', true).text('发送中...');
    
    // 发送GET请求到后端获取验证码
    $.get(`/auth/send_email_captcha`, {email: email})
        .done(function(data) {
            // console.log('Received response:', data);
            if (data.code === 200) {
                startCountdown(countdownTime);
            } else {
                alert(`发送失败: ${data.msg}`);
            }
        })
        .fail(function(xhr, status, error) {
            alert('发送验证码时出现错误：' + error);
        })
        .always(function() {
            // 恢复按钮状态（如果倒计时未启动）
            if (!$('#get-captcha-btn').prop('disabled')) {
                $('#get-captcha-btn').prop('disabled', false).text('获取验证码');
            }
        });
}

// 启动倒计时
function startCountdown(seconds) {
    let countdown = seconds;
    const button = $('#get-captcha-btn');
    
    // 禁用按钮
    button.prop('disabled', true);
    
    // 设置倒计时结束时间
    const cooldownEnd = new Date().getTime() + seconds * 1000;
    localStorage.setItem('captchaCooldown', cooldownEnd);
    
    // 启动定时器
    const timer = setInterval(function() {
        countdown--;
        if (countdown > 0) {
            button.text(`${countdown}s`);
        } else {
            // 倒计时结束
            clearInterval(timer);
            button.prop('disabled', false).text('获取验证码');
            // 清除localStorage中的倒计时
            localStorage.removeItem('captchaCooldown');
        }
    }, 1000);
}