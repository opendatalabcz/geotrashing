const POST_URL = document.currentScript.getAttribute('post_url'); 
const BIN_ID = document.currentScript.getAttribute('bin_id'); 
const FILL_PERC = document.currentScript.getAttribute('fill_perc');
if (window.requestIdleCallback) {
    requestIdleCallback(function () {
        makePostWithFingerPrint(POST_URL, BIN_ID, FILL_PERC);
    })
} else {
    setTimeout(function () {
        makePostWithFingerPrint(POST_URL, BIN_ID, FILL_PERC);
}, 500)
}

function makePostWithFingerPrint(url, bin_id, fill_perc) {
    /* geolocation
    navigator.geolocation.getCurrentPosition(function (position) {
        console.log(position)
    });
    */ 
    Fingerprint2.get(function (components) {
        // Hash
        var not_used_fields = ["webgl", "canvas"]
        var hash_fingerprint = ""
        var dict_components = components.reduce(function(map, obj) {
            map[obj.key] = obj.value;
            return map;
        }, {});

        Object.keys(dict_components).sort().forEach(function(key) {
            if (!not_used_fields.includes(key)){
                hash_fingerprint += `${key} : ${dict_components[key]} \n`
            }
        });
        var hash_output = Fingerprint2.x64hash128(hash_fingerprint)

        // Device characteristics
        var parser = new UAParser();
        parser.setUA(dict_components['userAgent']);
        var ua_parsed = parser.getResult();
        var browser = `${ua_parsed.browser.name}:${ua_parsed.browser.version}`;
        var os = `${ua_parsed.os.name}:${ua_parsed.os.version}`;
        var device =`${ua_parsed.device.vendor}:${ua_parsed.device.model}:${ua_parsed.device.type} `
        var cpu = ua_parsed.cpu.architecture;
        // Logging output
        // Post
        var post_body = `{
                    "id":${bin_id},
                    "fill_perc":${fill_perc},
                    "fingerprint":"${hash_output}",
                    "browser":"${browser}",
                    "os":"${os}",
                    "hw":"${device}",
                    "cpu":"${cpu}"
                        }`
        const request = new Request(url, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: post_body});
        fetch(request).then(response => {
            if (response.status === 200) {
                // console.log(response)
            } else {
                console.log('Something went wrong on api server!');
            }
        })
        .then(response => {
            //console.debug(response);
        }).catch(error => {
            console.error(error);
        });
    } )
}