window.onload = function () {
    const { createEditor, createToolbar } = window.wangEditor

    const editorConfig = {
        placeholder: 'Type here...',
        onChange(editor) {
            const html = editor.getHtml()
            console.log('editor content', html)
            // 也可以同步到 <textarea>
        },
    }

    const editor = createEditor({
        selector: '#editor-container',
        html: '<p><br></p>',
        config: editorConfig,
        mode: 'default', // or 'simple'
    })

    const toolbarConfig = {}

    const toolbar = createToolbar({
        editor,
        selector: '#toolbar-container',
        config: toolbarConfig,
        mode: 'default', // or 'simple'
    })

    $('#submit-btn').click(function(event) {
        event.preventDefault()

        let title = $('#title').val()
        let category = $('#category').val()
        let content = editor.getHtml()
        let csrfmiddlewaretoken = $('[name="csrfmiddlewaretoken"]').val()
        let data = {
            title: title,
            category: category,
            content: content,
            csrfmiddlewaretoken: csrfmiddlewaretoken,
        }
        $.post('/blog/pub', data)
            .then(res => {
                console.log(res)
                if (res['code'] === 200) {
                    let blog_id = res['data']['blog_id']
                    // 导航到对应的文章
                    window.location.href = '/blog/' + blog_id
                }
                else {
                    alert(res['msg'])
                }
            })
    })
}