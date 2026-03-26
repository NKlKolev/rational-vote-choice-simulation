import matplotlib.pyplot as plt
import streamlit as st

from engine import (
    get_representative_vote,
    find_workbook_path,
    load_bots_from_excel,
    load_json,
    generate_pdf_report,
)

st.set_page_config(page_title="Pustinyakovo Voting", layout="wide")

st.title("Гласуване на Върховния Конгрес на Република Пустиняково")

workbook_path = find_workbook_path()
if workbook_path:
    bots = load_bots_from_excel(workbook_path)
    st.success(f"Заредени народни представители от Excel: {workbook_path}")
else:
    bots = load_json("data/bots.json")
    st.warning("Заредени членове на Върховния Конгрес от JSON: data/bots.json")

st.write(f"Общ брой членове на Върховния Конгрес: {len(bots)}")

with st.expander("Покажи заредените членове на Върховния Конгрес"):
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
progress_text = st.empty()
progress_bar = st.progress(0)

def update_progress(current_step, total_steps):
    progress_text.write(f"Гласуване... {current_step}/{total_steps}")
    progress_bar.progress(current_step / total_steps)

simulation_output = get_representative_vote(
    bots,
    proposal,
    n_runs=100,
    pass_threshold=33,
    progress_callback=update_progress
)

results = simulation_output["results"]
totals = simulation_output["totals"]
party_totals = simulation_output["party_totals"]
bill_passed = simulation_output["bill_passed"]

progress_text.write("Гласуването приключи: 65/65")
progress_bar.progress(1.0)

st.subheader("Резултат")
st.write(f"ЗА: {totals['YES']}")
st.write(f"ПРОТИВ: {totals['NO']}")
st.write(f"ВЪЗДЪРЖАЛ СЕ: {totals['ABSTAIN']}")

if bill_passed:
    st.success("Законопроектът е ПРИЕТ")
else:
    st.error("Законопроектът НЕ Е ПРИЕТ")

st.subheader("Гласуване по партии")
for party, votes in party_totals.items():
    st.write(
        f"{party}: ЗА={votes['YES']} | ПРОТИВ={votes['NO']} | ВЪЗДЪРЖАЛ СЕ={votes['ABSTAIN']}"
    )

st.subheader("Гласуване по народни представители")

vote_labels = {
    "YES": "ЗА",
    "NO": "ПРОТИВ",
    "ABSTAIN": "ВЪЗДЪРЖАЛ СЕ"
}

member_rows = []
for result in results:
    member_rows.append({
        "Име": result["name"],
        "Партия": result["party"],
        "Вот": vote_labels.get(result["vote"], result["vote"]),
        "Резултат": result["score"],
        "Партиен натиск": result.get("party_pressure", 0.0),
        "Идеология": result.get("ideology_score", 0.0),
        "Значимост": result.get("salience_score", 0.0),
        "Отношения": result.get("relation_score", 0.0),
        "Шум": result.get("randomness", 0.0),
        "Обяснение": result["reason"],
    })

st.dataframe(member_rows, use_container_width=True)

st.subheader("Визуализация на гласуването")

vote_colors = {
    "YES": "green",
    "NO": "red",
    "ABSTAIN": "gray"
}

votes = [result["vote"] for result in results]
colors = [vote_colors.get(vote, "gray") for vote in votes]

n_cols = 13
x = []
y = []

for i in range(len(votes)):
    col = i % n_cols
    row = i // n_cols
    x.append(col)
    y.append(-row)

fig, ax = plt.subplots(figsize=(10, 4))
ax.scatter(x, y, s=500, c=colors, edgecolors="black")

for i, result in enumerate(results):
    ax.text(x[i], y[i], str(i + 1), ha="center", va="center", fontsize=8)

ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Гласуване по Места във Върховния Конгрес")
ax.set_frame_on(False)

st.pyplot(fig)

st.subheader("Доклад за гласуване във Върховния Конгрес")

generate_pdf_report(proposal, results, totals, party_totals, bill_passed)

with open("parliament_report.pdf", "rb") as pdf_file:
    st.download_button(
        label="Изтегли PDF доклада",
        data=pdf_file,
        file_name="parliament_report.pdf",
        mime="application/pdf"
    )
