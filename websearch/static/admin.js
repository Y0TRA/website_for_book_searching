document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#file').addEventListener('change', (e) => {
        console.log(e.target.files);
        document.querySelector('#files_info').innerHTML = 'Загружено файлов: ' + e.target.files.length
    })
})