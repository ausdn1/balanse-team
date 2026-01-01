import streamlit as st
import main, db_handler, random
import os

db_handler.init_db()
st.set_page_config(page_title="LoL 밸런스 측정기", layout="centered")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page != 'home':
    if st.sidebar.button("🏠 처음으로"):
        st.session_state.page = 'home'
        if 'my_room' in st.session_state: del st.session_state['my_room']
        st.rerun()

st.title("🏆 LoL 내전 맞밸런스")
st.write("---")

# --- 메인 홈 ---
if st.session_state.page == 'home':
    st.subheader("모드를 선택하세요")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📢 방 만들기 (방장)", use_container_width=True, type="primary"):
            st.session_state.page = 'host'; st.rerun()
    with c2:
        if st.button("🎮 입장하기 (게스트)", use_container_width=True):
            st.session_state.page = 'guest'; st.rerun()

# --- 호스트 화면 ---
elif st.session_state.page == 'host':
    if 'my_room' not in st.session_state:
        st.subheader("방장 정보를 입력하세요")
        h_id = st.text_input("닉네임#TAG", placeholder="예: 가나다#KR1")
        
        if h_id and "#" in h_id:
            url_id = h_id.replace('#', '-')
            st.link_button("🔍 내 딥롤 전적창 열기", f"https://www.deeplol.gg/summoner/KR/{url_id}")
            
            # 가이드 사진 및 팁
            if os.path.exists("guide.png"):
                st.image("guide.png", caption="위 사진의 숫자를 입력하세요")
            st.info("💡 딥롤 상단의 큰 'Deep Score' 숫자를 정수로 입력하세요!")

        h_score = st.number_input("내 AI-Score (1~100)", 0, 100, 0, step=1)
        
        if st.button("방 생성", use_container_width=True, type="primary"):
            if not h_id or "#" not in h_id:
                st.error("⚠️ 올바른 닉네임#TAG를 입력하세요.")
            elif h_score <= 0:
                st.error("⚠️ AI 점수를 입력하세요.")
            else:
                r_id = str(random.randint(1000, 9999))
                if db_handler.create_room(r_id):
                    db_handler.add_player(r_id, h_id, h_score, "None")
                    st.session_state['my_room'] = r_id
                    st.rerun()
    else:
        rid = st.session_state['my_room']
        st.success(f"방 번호: {rid}")
        players = db_handler.get_players(rid)
        st.subheader(f"참가자 현황 ({len(players)}/10)")
        for p in players:
            st.write(f"✅ **{p['name']}** : {int(p['score'])}점")
            
        if len(players) >= 10:
            if st.button("⚖️ 팀 밸런스 맞추기", type="primary", use_container_width=True):
                t_a, t_b, d = main.balance_teams(players[:10])
                st.balloons()
                col1, col2 = st.columns(2)
                with col1:
                    st.warning(f"🔵 A팀 (총점: {int(sum(x['score'] for x in t_a))})")
                    for p in t_a: st.write(f"**{p['name']}** ({int(p['score'])})")
                with col2:
                    st.success(f"🟢 B팀 (총점: {int(sum(x['score'] for x in t_b))})")
                    for p in t_b: st.write(f"**{p['name']}** ({int(p['score'])})")
                st.metric("양 팀 점수 차이", f"{int(abs(d))}점")
        else:
            if st.button("🔄 명단 새로고침"): st.rerun()

# --- 게스트 화면 ---
elif st.session_state.page == 'guest':
    st.header("🎮 게스트 입장")
    r_code = st.text_input("방 번호 4자리")
    if r_code and db_handler.check_room_exists(r_code):
        players = db_handler.get_players(r_code)
        if len(players) >= 10:
            st.error("🚫 방 정원이 초과되었습니다.")
        else:
            st.success("✅ 방을 찾았습니다.")
            g_id = st.text_input("내 닉네임#TAG", placeholder="예: 가나다#KR1")
            
            if g_id and "#" in g_id:
                url_id = g_id.replace('#', '-')
                st.link_button("🔍 내 전적창 열기", f"https://www.deeplol.gg/summoner/KR/{url_id}")
                
                # 가이드 사진 및 팁
                if os.path.exists("guide.png"):
                    st.image("guide.png", caption="딥롤 점수 확인 위치")
                st.warning("⚠️ 사진 속 주황색 네모 안의 숫자를 입력해 주세요!")

            g_score = st.number_input("AI-Score 입력", 0, 100, 0, step=1)
            
            if st.button("참가 완료", use_container_width=True, type="primary"):
                if not g_id or "#" not in g_id:
                    st.error("⚠️ 올바른 닉네임#TAG를 입력하세요.")
                elif g_score <= 0:
                    st.error("⚠️ AI 점수를 정확히 입력하세요.")
                elif db_handler.is_player_in_room(r_code, g_id):
                    st.warning("⚠️ 이미 등록된 유저입니다!")
                else:
                    db_handler.add_player(r_code, g_id, g_score, "None")
                    st.success("🎉 등록 성공! 방장 화면을 기다려주세요.")
                    st.balloons()
