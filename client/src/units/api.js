export async function callApi(path, options) {

    const overrideOptions = options || {
        method: 'GET'
    }
    if (!overrideOptions.headers) {
        overrideOptions.headers = {}
    }
    if (overrideOptions.body) {
        overrideOptions.body = JSON.stringify(overrideOptions.body)
        overrideOptions.headers['Content-Type'] = 'application/json'
    }
    return fetch(`http://localhost:3000/api/${path}`, overrideOptions)
        .then(response => {
            return response
        })
        .catch(error => {
            console.error(error)
            return Promise.reject(error)
        })
}
