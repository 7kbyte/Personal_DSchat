// ==================== 时间格式化 ====================
function fmtTime(ts) {
    if (!ts) return '';
    var d = new Date(ts), now = new Date();
    var hh = String(d.getHours()).padStart(2,'0'), mm = String(d.getMinutes()).padStart(2,'0');
    var time = hh + ':' + mm;
    if (d.toDateString() === now.toDateString()) return time;
    return String(d.getMonth()+1).padStart(2,'0') + '/' + String(d.getDate()).padStart(2,'0') + ' ' + time;
}

function fmtRelative(ts) {
    if (!ts) return '';
    var diff = Date.now() - ts;
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return Math.floor(diff/60000) + '分钟前';
    var d = new Date(ts), now = new Date();
    if (d.toDateString() === now.toDateString()) return String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
    return String(d.getMonth()+1).padStart(2,'0') + '/' + String(d.getDate()).padStart(2,'0');
}
