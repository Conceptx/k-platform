(function (name, path, ctx) {
    var latest, prev = name !== 'Keen' && window.Keen ? window.Keen : false;
    ctx[name] = ctx[name] || {
        ready: function (fn) {
            var h = document.getElementsByTagName('head')[0],
                s = document.createElement('script'),
                w = window,
                loaded;
            s.onload = s.onerror = s.onreadystatechange = function () {
                if ((s.readyState && !(/^c|loade/.test(s.readyState))) || loaded) {
                    return
                }
                s.onload = s.onreadystatechange = null;
                loaded = 1;
                latest = w.Keen;
                if (prev) {
                    w.Keen = prev
                } else {
                    try {
                        delete w.Keen
                    } catch (e) {
                        w.Keen = void 0
                    }
                }
                ctx[name] = latest;
                ctx[name].ready(fn)
            };
            s.async = 1;
            s.src = path;
            h.parentNode.insertBefore(s, h)
        }
    }
})('KeenAsync', 'https://d26b395fwzu5fz.cloudfront.net/keen-tracking-1.4.2.min.js', this);

KeenAsync.ready(function () {
    var client = new KeenAsync({
        projectId: '5badffe1c9e77c00012d481a',
        writeKey: '941C08DE5528948614884DACD46A2769BF3DAA1F5DCC327E3C99768B5E75300A5936ECA1768585FAC60C5B9A0ECA4087606EA574A8FD02A1135D77FF322148B77686AA157CC63FDED21EC58E69A9394B5655105F9142C72541982C677FF89D6F'
    });

    client.initAutoTracking();
});