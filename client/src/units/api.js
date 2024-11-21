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
    return fetch(`http://${window.location.host}/api/${path}`, overrideOptions)
        .then(async response => {
            if (!response.ok) {
                throw new Error(`服务器错误: ${response.status}`);
            }
            return response;
        })
        .catch(error => {
            console.error('callApi', error)
            return Promise.reject(error)
        })
}
