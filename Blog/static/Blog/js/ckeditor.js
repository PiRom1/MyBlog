//import { ClassicEditor } from 'https://cdn.ckeditor.com/ckeditor5/36.0.1/classic/ckeditor5.js';

// Editor Configuration
const editorConfig = {
    toolbar: {
        items: [
            'undo',
            'redo',
            '|',
            'bold',
            'italic',
            'underline',
            'strikethrough',
            'code',
            '|',
            'link',
            'insertTable',
            'blockQuote',
            '|',
            'bulletedList',
            'numberedList',
            'todoList',
            'outdent',
            'indent'
        ],
        shouldNotGroupWhenFull: false,
    },
    language: 'fr', // Set editor language to French
    link: {
        addTargetToExternalLinks: true,
        defaultProtocol: 'https://',
        decorators: {
            toggleDownloadable: {
                mode: 'manual',
                label: 'Downloadable',
                attributes: {
                    download: 'file',
                },
            },
        },
    },
    list: {
        properties: {
            styles: true,
            startIndex: true,
            reversed: true,
        },
    },
    placeholder: 'Type or paste your content here!',
    table: {
        contentToolbar: [
            'tableColumn',
            'tableRow',
            'mergeTableCells',
            'tableProperties',
            'tableCellProperties'
        ],
    },
};

window.editorInstance = null;

// Create CKEditor Instance
function createEditor() {
    ClassicEditor
        .create(document.querySelector('#message_html'), editorConfig)
        .then(editor => {
            window.editorInstance = editor;
        })
        .catch(error => {
            console.error(error);
        });
}

// Initialize the editor
createEditor();
