from engine import run_vote, count_votes, count_votes_by_party
import streamlit as st

from engine import find_workbook_path, load_bots_from_excel, load_json

st.set_page_config(page_title="Pustinyakovo Voting", layout="wide")

st.title("Симулация на парламентарно гласуване")

workbook_path = find_workbook_path()
if workbook_path:
    bots = load_bots_from_excel(workbook_path)
    st.success(f"Заредени народни представители от Excel: {workbook_path}")
else:
    bots = load_json("data/bots.json")
    st.warning("Заредени народни представители от JSON: data/bots.json")

st.write(f"Общ брой народни представители: {len(bots)}")

with st.expander("Покажи заредените народни представители"):
    for bot in bots:
        st.write(f"{bot['name']} ({bot['party']})")

st.subheader("Данни за законопроекта")

title = st.text_input("Заглавие на предложението")
bill_id = st.text_input("Уникален номер на законопроекта")
description = st.text_area("За какво е законопроектът")
changes = st.text_area("Какво променя законопроектът")

proposal_type = st.selectbox(
    "Тип предложение",
    ["policy", "pm_election"]
)

party_names = sorted(list({bot["party"] for bot in bots}))

proposed_by_party = st.selectbox(
    "Вносител на предложението",
    [""] + party_names
)

candidate_party = ""
if proposal_type == "pm_election":
    candidate_party = st.selectbox(
        "Партия на кандидата",
        [""] + party_names
    )

if proposal_type == "policy":
    st.subheader("Характеристики на политиката")

    col1, col2, col3 = st.columns(3)

    with col1:
        social_progressive_traditionalist = st.slider(
            "Прогресивни (-1) / традиционни (+1) норми",
            -1.0, 1.0, 0.0, 0.05
        )
        civil_rights = st.slider(
            "Граждански права",
            -1.0, 1.0, 0.0, 0.05
        )
        family_values_conflict = st.slider(
            "Конфликт със семейни ценности",
            -1.0, 1.0, 0.0, 0.05
        )
        economic_left_right = st.slider(
            "Икономически лява (-1) / дясна (+1)",
            -1.0, 1.0, 0.0, 0.05
        )
        economy = st.slider(
            "Икономическа важност",
            0.0, 1.0, 0.0, 0.05
        )

    with col2:
        security = st.slider(
            "Сигурност / контрол",
            -1.0, 1.0, 0.0, 0.05
        )
        infrastructure = st.slider(
            "Инфраструктура",
            0.0, 1.0, 0.0, 0.05
        )
        public_spending = st.slider(
            "Публични разходи",
            -1.0, 1.0, 0.0, 0.05
        )
        regional_development = st.slider(
            "Регионално развитие",
            0.0, 1.0, 0.0, 0.05
        )
        controversy = st.slider(
            "Спорност",
            0.0, 1.0, 0.0, 0.05
        )

    with col3:
        public_support = st.slider(
            "Обществена подкрепа",
            -1.0, 1.0, 0.0, 0.05
        )
        fiscal_impact = st.slider(
            "Бюджетен ефект",
            -1.0, 1.0, 0.0, 0.05
        )
        international_alignment = st.slider(
            "Международно / европейско съответствие",
            -1.0, 1.0, 0.0, 0.05
        )
        urgency = st.slider(
            "Спешност",
            0.0, 1.0, 0.0, 0.05
        )

st.subheader("Позиции на партиите")

party_positions = {}
party_cols = st.columns(min(3, len(party_names)) if party_names else 1)

for i, party in enumerate(party_names):
    with party_cols[i % len(party_cols)]:
        party_positions[party] = st.slider(
            party,
            -1.0, 1.0, 0.0, 0.05,
            key=f"party_{party}"
        )

st.divider()

if st.button("Пусни гласуване"):
    # Build proposal
    proposal = {
        "title": title,
        "bill_id": bill_id,
        "description": description,
        "changes": changes,
        "type": proposal_type,
        "proposed_by_party": proposed_by_party,
        "candidate_party": candidate_party,
        "effects": {},
        "party_positions": party_positions
    }

    if proposal_type == "policy":
        proposal["effects"] = {
            "social_progressive_traditionalist": social_progressive_traditionalist,
            "civil_rights": civil_rights,
            "family_values_conflict": family_values_conflict,
            "economic_left_right": economic_left_right,
            "economy": economy,
            "security": security,
            "infrastructure": infrastructure,
            "public_spending": public_spending,
            "regional_development": regional_development,
            "controversy": controversy,
            "public_support": public_support,
            "fiscal_impact": fiscal_impact,
            "international_alignment": international_alignment,
            "urgency": urgency
        }

    # Run vote
    results = run_vote(bots, proposal)
    totals = count_votes(results)
    party_totals = count_votes_by_party(results)

    st.subheader("Резултат")

    st.write(f"ЗА: {totals['YES']}")
    st.write(f"ПРОТИВ: {totals['NO']}")
    st.write(f"ВЪЗДЪРЖАЛ СЕ: {totals['ABSTAIN']}")

    if totals["YES"] >= 33:
        st.success("Законопроектът е ПРИЕТ")
    else:
        st.error("Законопроектът НЕ Е ПРИЕТ")

    st.subheader("Гласуване по партии")
    for party, votes in party_totals.items():
        st.write(
            f"{party}: ЗА={votes['YES']} | ПРОТИВ={votes['NO']} | ВЪЗДЪРЖАЛ СЕ={votes['ABSTAIN']}"
        )