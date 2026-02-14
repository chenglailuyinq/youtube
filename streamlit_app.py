import streamlit as st
import yt_dlp
import os
import tempfile

def get_video_info(url):
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def main():
    st.set_page_config(page_title="Ultimate YT Downloader", page_icon="🎥")
    st.title("🎥 YouTube 高画質ダウンローダー")
    st.write("URLを入力して、画質・音質を選択してください。最高画質は自動で結合されます。")

    url = st.text_input("YouTube動画のURLを入力:", placeholder="https://www.youtube.com/watch?v=...")

    if url:
        try:
            with st.spinner("情報を取得中..."):
                info = get_video_info(url)
                formats = info.get('formats', [])
                title = info.get('title', 'video')
                
            st.subheader(f"🎵 {title}")

            # 選択肢の整理
            video_options = []
            audio_options = []
            
            for f in formats:
                ext = f.get('ext')
                resolution = f.get('resolution')
                vcodec = f.get('vcodec')
                acodec = f.get('acodec')
                fid = f.get('format_id')

                # 映像のみ (googlevideo.com 直リンク含む)
                if vcodec != 'none' and acodec == 'none':
                    video_options.append({
                        "label": f"🎥 映像: {resolution} ({ext}) - ID:{fid}",
                        "id": fid,
                        "ext": ext
                    })
                # 音声のみ
                elif vcodec == 'none' and acodec != 'none':
                    audio_options.append({
                        "label": f"🔊 音声: {f.get('abr')}kbps ({ext}) - ID:{fid}",
                        "id": fid,
                        "ext": ext
                    })

            # ユーザー選択 UI
            mode = st.radio("ダウンロードモードを選択:", ["映像+音声 (最高画質結合)", "映像のみ (単品)", "音声のみ (単品)"])

            selected_video = None
            selected_audio = None

            if mode == "映像+音声 (最高画質結合)":
                v_labels = [opt["label"] for opt in video_options]
                a_labels = [opt["label"] for opt in audio_options]
                v_choice = st.selectbox("映像画質を選択:", v_labels)
                a_choice = st.selectbox("音声品質を選択:", a_labels)
                selected_video = next(opt for opt in video_options if opt["label"] == v_choice)
                selected_audio = next(opt for opt in audio_options if opt["label"] == a_choice)
                format_str = f"{selected_video['id']}+{selected_audio['id']}"
                out_ext = "mp4" # 結合時はmp4が一般的

            elif mode == "映像のみ (単品)":
                v_labels = [opt["label"] for opt in video_options]
                v_choice = st.selectbox("映像を選択:", v_labels)
                selected_video = next(opt for opt in video_options if opt["label"] == v_choice)
                format_str = selected_video['id']
                out_ext = selected_video['ext']

            else: # 音声のみ
                a_labels = [opt["label"] for opt in audio_options]
                a_choice = st.selectbox("音声を選択:", a_labels)
                selected_audio = next(opt for opt in audio_options if opt["label"] == a_choice)
                format_str = selected_audio['id']
                out_ext = selected_audio['ext']

            if st.button("ダウンロード準備開始"):
                with st.spinner("サーバーで処理中... (高画質結合には時間がかかります)"):
                    # 一時ファイル用ディレクトリ
                    with tempfile.TemporaryDirectory() as tmpdir:
                        output_path = os.path.join(tmpdir, f"output.{out_ext}")
                        
                        ydl_download_opts = {
                            'format': format_str,
                            'outtmpl': output_path,
                            'merge_output_format': 'mp4' if mode == "映像+音声 (最高画質結合)" else None,
                            'quiet': True,
                        }

                        with yt_dl_YoutubeDL(ydl_download_opts) as ydl:
                            # 処理実行
                            ydl.download([url])
                            
                        # 完成したファイルをバイナリで読み込み
                        with open(output_path, "rb") as f:
                            btn = st.download_button(
                                label="PC/スマホに保存する",
                                data=f,
                                file_name=f"{title}.{out_ext}",
                                mime=f"video/{out_ext}" if "映像" in mode else f"audio/{out_ext}"
                            )
                            st.success("準備完了！上のボタンを押して保存してください。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# yt_dlpのクラス呼び出しを修正
from yt_dlp import YoutubeDL as yt_dl_YoutubeDL

if __name__ == "__main__":
    main()
