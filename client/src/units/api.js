export async function callApi(path, options) {
    const overrideOptions = options || {
        method: 'GET'
    }
    return fetch(`http://127.0.0.1:3000/api/${path}`, overrideOptions)
}
