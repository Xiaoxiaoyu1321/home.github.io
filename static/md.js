/* ==========================================================================
   Next_md 分支：Material Design 3 主页脚本
   功能：一言语录 · 随机音乐播放器（悬浮弹窗）· FAB 开关
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

    // ---------- 音乐播放器（悬浮弹窗） ----------
    var modal = document.getElementById("player-modal");
    var fab = document.getElementById("music-fab");
    var closeBtn = document.getElementById("player-modal-close");
    var errorEl = document.getElementById("player-error");
    var ap = null;
    var inited = false;

    function showError() {
        if (errorEl) errorEl.hidden = false;
    }

    // 首次打开弹窗时初始化播放器（此时弹窗可见，容器宽度正常）
    function initPlayer() {
        inited = true;
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
                        container: document.getElementById("aplayer-inner"),
                        audio: audio,
                        fixed: false,     // 弹窗内普通模式
                        autoplay: true,   // 用户点击 FAB 后自动播放
                        order: music_order,
                        listFolded: false,
                        volum: music_volume,
                        mini: false,
                        lrcType: 3,
                        preload: "auto",
                        loop: music_loop
                    });
                } catch (e) {
                    console.error("APlayer 初始化失败", e);
                    showError();
                }
            },
            error: function () {
                console.warn("Meting API 不可用，播放器未加载");
                showError();
            }
        });
    }

    function openModal() {
        if (!inited) initPlayer();
        modal.hidden = false;
        document.body.style.overflow = "hidden";
        if (ap) ap.play();
    }

    function closeModal() {
        modal.hidden = true;
        document.body.style.overflow = "";
        if (ap) ap.pause();
    }

    if (fab) fab.addEventListener("click", openModal);
    if (closeBtn) closeBtn.addEventListener("click", closeModal);

    // 点击遮罩关闭
    if (modal) {
        modal.addEventListener("click", function (e) {
            if (e.target === modal) closeModal();
        });
    }

    // Esc 关闭
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closeModal();
    });
})();
