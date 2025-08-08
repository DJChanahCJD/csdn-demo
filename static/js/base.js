// 初始化消息自动消失功能
function initializeMessages() {
    // 为所有消息项设置5秒后自动消失
    $('.message-item').each(function() {
        const $message = $(this);
        setTimeout(function() {
            $message.addClass('hide');
            // 动画结束后移除元素
            setTimeout(function() {
                $message.remove();
            }, 300);
        }, 5000);
    });
}