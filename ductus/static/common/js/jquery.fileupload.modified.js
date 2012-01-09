/* Modified (stripped down) jQuery file upload.  Originally based on:
 *
 * jQuery File Upload Plugin 2.0
 *
 * Copyright 2010, Sebastian Tschan, AQUANTUM
 * Licensed under the MIT license:
 * http://creativecommons.org/licenses/MIT/
 *
 * https://blueimp.net
 * http://www.aquantum.de
 */

/*jslint browser: true */
/*global File, FileReader, FormData, unescape, jQuery */

(function ($) {

    $.ductusFileUpload = function (settings) {
        var default_settings = {
            url: '',
            method: 'post',
            fieldName: 'file',
            multipart: true,
            withCredentials: false
        },
        undef = 'undefined',
        protocolRegExp = /^http(s)?:\/\//,

        initUploadEventHandlers = function (files, index, xhr, settings) {
            if (typeof settings.onProgress === 'function') {
                xhr.upload.onprogress = function (e) {
                    settings.onProgress(e, files, index, xhr, settings);
                };
            }
            if (typeof settings.onLoad === 'function') {
                xhr.onload = function (e) {
                    settings.onLoad(e, files, index, xhr, settings);
                };
            }
            if (typeof settings.onAbort === 'function') {
                xhr.onabort = function (e) {
                    settings.onAbort(e, files, index, xhr, settings);
                };
            }
            if (typeof settings.onError === 'function') {
                xhr.onerror = function (e) {
                    settings.onError(e, files, index, xhr, settings);
                };
            }
        },

        getFormData = function (settings) {
            return [];
        },

        buildMultiPartFormData = function (boundary, file, fileContent, fields) {
            var doubleDash = '--',
                crlf     = '\r\n',
                formData = '';
            $.each(fields, function (index, field) {
                formData += doubleDash + boundary + crlf +
                    'Content-Disposition: form-data; name="' +
                    unescape(encodeURIComponent(field.name)) +
                    '"' + crlf + crlf +
                    unescape(encodeURIComponent(field.value)) + crlf;
            });
            formData += doubleDash + boundary + crlf +
                'Content-Disposition: form-data; name="' +
                unescape(encodeURIComponent(settings.fieldName)) +
                '"; filename="' + unescape(encodeURIComponent(file.name)) + '"' + crlf +
                'Content-Type: ' + file.type + crlf + crlf +
                fileContent + crlf +
                doubleDash + boundary + doubleDash + crlf;
            return formData;
        },

        isSameDomain = function (url) {
            if (protocolRegExp.test(url)) {
                var host = location.host,
                    indexStart = location.protocol.length + 2,
                    index = url.indexOf(host, indexStart),
                    pathIndex = index + host.length;
                if ((index === indexStart || index === url.indexOf('@', indexStart) + 1) && (
                    url.length === pathIndex || $.inArray(url.charAt(pathIndex), ['/', '?', '#']))) {
                    return true;
                }
                return false;
            }
            return true;
        },

        uploadFile = function (files, index, xhr, settings) {
            var sameDomain = isSameDomain(settings.url),
                file = files[index],
                formData, fileReader;
            initUploadEventHandlers(files, index, xhr, settings);
            xhr.open(settings.method, settings.url, true);
            if (sameDomain) {
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken')); // modified for ductus to deal with django csrf handling
            } else if (settings.withCredentials) {
                xhr.withCredentials = true;
            }
            if (!settings.multipart) {
                if (sameDomain) {
                    xhr.setRequestHeader('X-File-Name', unescape(encodeURIComponent(file.name)));
                }
                xhr.setRequestHeader('Content-Type', file.type);
                xhr.send(file);
            } else {
                if (file.hasOwnProperty('recordedContent')) {
                    // for flash recorded audio only, which is passed as a string from flash to JS
                    var boundary = '12345678901234567890';
                    xhr.setRequestHeader('Content-Type', 'multipart/form-data; boundary=' + boundary);

                    var body = buildMultiPartFormData(
                                    boundary,
                                    file,
                                    file.recordedContent,
                                    getFormData(settings)
                                    );

                    var audioByteArray = new Uint8Array(body.length);
                    for (var i=0; i< audioByteArray.length; i++) {
                         audioByteArray[i] = body.charCodeAt(i);
                    }
                    xhr.send(audioByteArray.buffer);
                } else if (typeof FormData !== undef) {
                    formData = new FormData();
                    $.each(getFormData(settings), function (index, field) {
                        formData.append(field.name, field.value);
                    });
                    formData.append(settings.fieldName, file);
                    xhr.send(formData);
                } else if (typeof FileReader !== undef) {
                    fileReader = new FileReader();
                    fileReader.onload = function (e) {
                        var fileContent = e.target.result,
                            boundary = '----MultiPartFormBoundary' + (new Date()).getTime();
                        xhr.setRequestHeader('Content-Type', 'multipart/form-data; boundary=' + boundary);
                        xhr.sendAsBinary(buildMultiPartFormData(
                            boundary,
                            file,
                            fileContent,
                            getFormData(settings)
                        ));
                    };
                    fileReader.readAsBinaryString(file);
                } else {
                    $.error('Browser does neither support FormData nor FileReader interface');
                }
            }
        },

        handleFile = function (files, index) {
            var xhr = new XMLHttpRequest();
            if (typeof settings.init === 'function') {
                settings.init(files, index, xhr, function (options) {
                    uploadFile(files, index, xhr, $.extend({}, settings, options));
                }, settings);
            } else {
                uploadFile(files, index, xhr, settings);
            }
        },

        handleFiles = function (files) {
            for (var i = 0; i < files.length; i += 1) {
                handleFile(files, i);
            }
        };

        settings = $.extend({}, default_settings, settings || {});
        return {handleFiles: handleFiles};
    };

}(jQuery));
