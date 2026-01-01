import streamlit as st
import main, db_handler, random

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

if st.session_state.page == 'home':
    st.subheader("모드를 선택하세요")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📢 방 만들기 (방장)", use_container_width=True, type="primary"):
            st.session_state.page = 'host'; st.rerun()
    with c2:
        if st.button("🎮 입장하기 (게스트)", use_container_width=True):
            st.session_state.page = 'guest'; st.rerun()

elif st.session_state.page == 'host':
    if 'my_room' not in st.session_state:
        st.subheader("방장 정보를 입력하세요")
        h_id = st.text_input("닉네임#TAG")
        
        if h_id:
            url_id = h_id.replace('#', '-')
            deeplol_url = f"https://www.deeplol.gg/summoner/KR/{url_id}"
            st.link_button("🔍 내 딥롤 전적창 열기", deeplol_url)
            
        # [수정] 범위를 0~100으로 변경
        h_score = st.number_input("내 AI-Score (0~100)", 0, 100, 50, step=1)
        
        if st.button("방 생성", use_container_width=True, type="primary"):
            if "#" in h_id:
                r_id = str(random.randint(1000, 9999))
                if db_handler.create_room(r_id):
                    db_handler.add_player(r_id, h_id, h_score, "None")
                    st.session_state['my_room'] = r_id
                    st.rerun()
            else: st.error("태그(#)를 포함해 주세요!")
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
                    sum_a = int(sum(x['score'] for x in t_a))
                    st.warning(f"🔵 A팀 (총점: {sum_a})")
                    for p in t_a: st.write(f"**{p['name']}** ({int(p['score'])})")
                with col2:
                    sum_b = int(sum(x['score'] for x in t_b))
                    st.success(f"🟢 B팀 (총점: {sum_b})")
                    for p in t_b: st.write(f"**{p['name']}** ({int(p['score'])})")
                st.metric("양 팀 점수 차이", f"{int(abs(d))}점")
        else:
            if st.button("🔄 명단 새로고침"): st.rerun()

elif st.session_state.page == 'guest':
    r_code = st.text_input("방 번호 4자리")
    if r_code and db_handler.check_room_exists(r_code):
        g_id = st.text_input("내 닉네임#TAG")
        if g_id:
            url_id = g_id.replace('#', '-')
            deeplol_url = f"https://www.deeplol.gg/summoner/KR/{url_id}"
            st.link_button("🔍 내 전적창 열기", deeplol_url)
            
        # [수정] 범위를 0~100으로 변경
        g_score = st.number_input("딥롤 AI-Score (0~100)", 0, 100, 50, step=1)
        
        if st.button("참가 완료", use_container_width=True, type="primary"):
            if "#" in g_id:
                db_handler.add_player(r_code, g_id, g_score, "None")
                st.success("등록되었습니다!")
            else: st.error("태그(#)를 포함해 주세요!")