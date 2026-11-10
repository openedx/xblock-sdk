/* Javascript for {{cookiecutter.class_name}}. */
function {{cookiecutter.class_name}}(runtime, element, data) {
    (async () => {
        const {renderBlock} = await import(data.url);
        renderBlock(element, runtime, data);
    })();
}
