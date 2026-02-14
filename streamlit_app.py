import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="YouTube Downloader", page_icon="🎥")

st.title("🎥 YouTube 高画質ダウンローダー")
st.write("URLを入力して、お好みの画質・形式でダウンロードできます。")

# URL入力
url = st.text_input("YouTube URLを入力してください:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    with st.spinner("動画情報を取得中..."):
        ydl_opts = {'quiet': True, 'no_warnings': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                title = info.get('title', 'video')
                
                st.subheader(f"作品名: {title}")
                
                # 選択肢の作成
                options = []
                # 1. 音声のみ
                options.append({"label": "音声のみ (mp3/m4a)", "format_id": "bestaudio/best", "ext": "mp3"})
                
                # 2. 映像+音声 (結合済み or 高画質結合)
                # 一般的な画質をリストアップ
                res_list = ["2160", "1440", "1080", "720", "480", "360"]
                seen_res = set()
                
                for f in formats:
                    res = f.get('height')
                    if res and str(res) in res_list and res not in seen_res:
                        options.append({
                            "label": f"動画: {res}p (最高画質結合)",
                            "format_id": f"bestvideo[height<={res}]+bestaudio/best",
                            "ext": "mp4"
                        })
                        seen_res.add(res)

                # ユーザー選択 UI
                choice = st.selectbox("ダウンロード形式を選択:", options, format_func=lambda x: x['label'])
                
                if st.button("ダウンロード準備開始"):
                    with st.spinner("サーバーで処理中... (高画質の場合は結合に時間がかかります)"):
                        # 一時ディレクトリで作業
                        with tempfile.TemporaryDirectory() as tmpdirname:
                            output_template = os.path.join(tmpdirname, f"{title}.%(ext)s")
                            
                            dl_opts = {
                                'format': choice['format_id'],
                                'outtmpl': output_template,
                                'merge_output_format': 'mp4' if choice['ext'] == 'mp4' else None,
                                'postprocessors': [{
                                    'key': 'FFmpegExtractAudio',
                                    'preferredcodec': 'mp3',
                                    'preferredquality': '192',
                                } if choice['ext'] == 'mp3' else {
                                    'key': 'FFmpegVideoConvertor',
                                    'preferedformat': 'mp4',
                                }],
                                'quiet': False,
                            }
                            
                            with yt_dlp.YoutubeDL(dl_opts) as ydl_dl:
                                ydl_dl.download([url])
                            
                            # ダウンロードされたファイルを探す
                            files = os.listdir(tmpdirname)
                            if files:
                                target_file = os.path.join(tmpdirname, files[0])
                                with open(target_file, "rb") as f:
                                    st.download_button(
                                        label="📥 PC/スマホへ保存",
                                        data=f,
                                        file_name=files[0],
                                        mime="video/mp4" if choice['ext'] == 'mp4' else "audio/mpeg"
                                    )
                                st.success("準備が完了しました！上のボタンを押して保存してください。")
                                
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

st.markdown("---")
st.caption("利用規約を遵守し、個人利用の範囲でご使用ください。")
