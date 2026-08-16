/* ==========================================================================
   Next_md 分支：Material Design 3 主页脚本
   功能：一言语录 · 网易云播放器（吸底）· 音乐 FAB 开关
   ========================================================================== */

(function () {
    "use strict";

    // ---------- 一言 ----------
    fetch(hitokoto_api)
        .then(function (res) {
            return res.json();
        })
        .then(function (data) {
            var el = document.getElementById("hitokoto_text");
            if (el) {
                el.textContent = data.hitokoto;
                el.title = "一言 · 点击查看";
                el.style.cursor = "pointer";
                el.onclick = function () {
                    window.open("https://hitokoto.cn/?uuid=" + data.uuid, "_blank");
                };
            }
        })
        .catch(function () {
            var el = document.getElementById("hitokoto_text");
            if (el) el.textContent = ":D 一言获取失败";
        });

    // ---------- 音乐播放器（吸底） ----------
    var ap = null;

    $.ajax({
        url: meting_music_api,
        data: {
            server: music_server,
            type: music_type,
            id: music_id
        },
        dataType: "json",
        success: function (audio) {
            try {
                ap = new APlayer({
                    container: document.getElementById("aplayer-fixed"),
                    audio: audio,
                    fixed: true,      // 吸底模式
                    autoplay: music_autoplay,
                    order: music_order,
                    listFolded: true,
                    volum: music_volume,
                    mini: true,
                    lrcType: 3,
                    preload: "auto",
                    loop: music_loop
                });
            } catch (e) {
                console.error("APlayer 初始化失败", e);
            }
        },
        error: function () {
            console.warn("Meting API 不可用，播放器未加载");
        }
    });

    // ---------- 音乐 FAB：显示/隐藏播放器 ----------
    var fab = document.getElementById("music-fab");
    if (fab) {
        fab.addEventListener("click", function () {
            var player = document.getElementById("aplayer-fixed");
            if (!player) return;
            var hidden = player.classList.toggle("hidden");
            if (ap) {
                if (hidden) ap.pause();
                else ap.play();
            }
        });
    }
})();
