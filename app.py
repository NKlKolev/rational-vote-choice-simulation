import matplotlib.pyplot as plt
import streamlit as st

from engine import (
    get_representative_vote,
    calculate_party_positions,
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

TOTAL_SEATS = 120
st.write(f"Общ брой членове на Върховния Конгрес: {len(bots)} / {TOTAL_SEATS}")

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
    ["policy", "region_policy", "pm_election"],
    format_func=lambda x: {
        "policy": "Обикновен законопроект",
        "region_policy": "Регионално-специфичен законопроект",
        "pm_election": "Избор на министър-председател",
    }.get(x, x)
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

region_policy_data = {}

REGIONS = [
    "Столична Община",
    "Сапарева Баня",
    "Михайловград",
    "Банкя",
    "Банско",
    "Варна",
    "Търново",
    "Перник",
]

INDICATOR_LABELS = {
    "economy": "Икономика",
    "education": "Образование",
    "urbanization": "Урбанизация",
    "fiscal_capacity": "Фискален капацитет",
    "state_dependency": "Зависимост от централната държава",
    "infrastructure": "Инфраструктура",
    "public_services": "Обществени услуги",
    "industrial_output": "Индустриално производство",
    "unemployment": "Безработица",
    "unrest": "Обществено напрежение",
    "corruption": "Корупция",
    "turnout": "Избирателна активност",
    "political_volatility": "Политическа волатилност",
    "traditionalism": "Традиционализъм",
    "progressivism": "Прогресивизъм",
    "regime_trust": "Доверие в режима",
    "opposition_strength": "Сила на опозицията",
    "patronage": "Патронаж",
    "local_identity": "Местна идентичност",
    "muslim_share": "Мюсюлманско население",
}

POLICY_TEMPLATE_LABELS = {
    "infrastructure_investment": "Инфраструктурна инвестиция",
    "employment_program": "Програма за заетост",
    "anti_corruption_reform": "Антикорупционна реформа",
    "social_program": "Социална програма",
    "industrial_subsidy": "Индустриална субсидия",
    "security_measure": "Извънредна мярка за сигурност",
    "manual_regional_effect": "Ръчно зададен регионален ефект",
}

RECOMMENDED_TEMPLATE_BY_INDICATOR = {
    "infrastructure": "infrastructure_investment",
    "unemployment": "employment_program",
    "corruption": "anti_corruption_reform",
    "public_services": "social_program",
    "industrial_output": "industrial_subsidy",
    "unrest": "security_measure",
    "regime_trust": "social_program",
    "opposition_strength": "security_measure",
    "patronage": "anti_corruption_reform",
    "local_identity": "manual_regional_effect",
}

INTENSITY_LABELS = {
    "low": "Ниска",
    "medium": "Средна",
    "high": "Висока",
    "emergency": "Извънредна",
}

FUNDING_SOURCES = [
    "Бюджет",
    "Дълг",
    "Аварийен резерв",
    "Символично/регулаторно решение",
]

DEFAULT_COST_BY_INTENSITY = {
    "low": 150,
    "medium": 400,
    "high": 750,
    "emergency": 1200,
}

DEFAULT_EFFECT_BY_TEMPLATE = {
    "infrastructure_investment": {"infrastructure": 5, "economy": 2, "corruption": 1},
    "employment_program": {"unemployment": -5, "regime_trust": 3, "economy": 2},
    "anti_corruption_reform": {"corruption": -5, "regime_trust": 2, "patronage": -3},
    "social_program": {"public_services": 4, "unrest": -3, "regime_trust": 2},
    "industrial_subsidy": {"industrial_output": 5, "economy": 3, "unemployment": -3},
    "security_measure": {"unrest": -4, "security": 3, "civil_rights": -2},
}

if proposal_type == "region_policy":
    st.subheader("Регионално-специфичен законопроект")

    region_col1, region_col2, region_col3 = st.columns(3)

    with region_col1:
        target_region = st.selectbox("Целева област", REGIONS)
        target_indicator = st.selectbox(
            "Целеви проблем / показател",
            list(INDICATOR_LABELS.keys()),
            format_func=lambda x: f"{INDICATOR_LABELS[x]} ({x})"
        )

    recommended_template = RECOMMENDED_TEMPLATE_BY_INDICATOR.get(
        target_indicator,
        "manual_regional_effect"
    )

    with region_col2:
        policy_template = st.selectbox(
            "Тип политически шаблон",
            list(POLICY_TEMPLATE_LABELS.keys()),
            index=list(POLICY_TEMPLATE_LABELS.keys()).index(recommended_template),
            format_func=lambda x: f"{POLICY_TEMPLATE_LABELS[x]} ({x})"
        )
        policy_intensity = st.selectbox(
            "Интензитет",
            list(INTENSITY_LABELS.keys()),
            index=1,
            format_func=lambda x: INTENSITY_LABELS[x]
        )

    with region_col3:
        fiscal_amount_millions = st.number_input(
            "Фискална сума в млн.",
            min_value=0,
            value=DEFAULT_COST_BY_INTENSITY[policy_intensity],
            step=50
        )
        funding_source = st.selectbox("Източник на финансиране", FUNDING_SOURCES)

    target_problem = st.text_input(
        "Описание на проблема от картата",
        value=f"Проблем с показател: {INDICATOR_LABELS[target_indicator]} в {target_region}"
    )

    manual_change_value = 0
    if policy_template == "manual_regional_effect":
        manual_change_value = st.number_input(
            "Ръчна промяна на показателя",
            min_value=-20,
            max_value=20,
            value=5,
            step=1
        )

    if not title:
        st.info("Съвет: добави заглавие на законопроекта горе, например: Закон за регионална заетост в Банкя.")

    expected_regional_effects = DEFAULT_EFFECT_BY_TEMPLATE.get(policy_template, {})
    if policy_template == "manual_regional_effect":
        expected_regional_effects = {target_indicator: manual_change_value}

    recommended_map_section = (
        "Прилагане на решение"
        if policy_template == "manual_regional_effect"
        else "Прилагане на политически шаблон"
    )

    fiscal_amount_meaning = (
        "Няма директен фискален разход"
        if funding_source == "Символично/регулаторно решение" and fiscal_amount_millions == 0
        else "Цена на регионалната програма"
    )

    region_policy_data = {
        "target_region": target_region,
        "target_problem": target_problem,
        "target_indicator": target_indicator,
        "target_indicator_label": INDICATOR_LABELS[target_indicator],
        "policy_template": policy_template,
        "policy_template_label": POLICY_TEMPLATE_LABELS[policy_template],
        "policy_intensity": policy_intensity,
        "policy_intensity_label": INTENSITY_LABELS[policy_intensity],
        "scope": "Една област",
        "fiscal_amount_millions": fiscal_amount_millions,
        "fiscal_amount_meaning": fiscal_amount_meaning,
        "funding_source": funding_source,
        "recommended_map_section": recommended_map_section,
        "expected_regional_effects": expected_regional_effects,
    }

if proposal_type in ["policy", "region_policy"]:
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
party_position_mode = st.radio(
    "Режим за позициите на партиите",
    ["Автоматично", "Ръчно"],
    horizontal=True
)

manual_party_positions = {}

if party_position_mode == "Автоматично":
    st.caption("Партийните позиции ще бъдат изчислени автоматично от системата.")
else:
    st.caption("Задай ръчно позициите на партиите.")
    party_cols = st.columns(min(3, len(party_names)) if party_names else 1)

    for i, party in enumerate(party_names):
        with party_cols[i % len(party_cols)]:
            manual_party_positions[party] = st.slider(
                party,
                -1.0, 1.0, 0.0, 0.05,
                key=f"party_{party}"
            )

st.divider()

pass_threshold = 61
if "last_vote_output" not in st.session_state:
    st.session_state.last_vote_output = None
if st.button("Пусни гласуване"):
    engine_proposal_type = "policy" if proposal_type == "region_policy" else proposal_type

    proposal = {
        "title": title,
        "bill_id": bill_id,
        "description": description,
        "changes": changes,
        "type": engine_proposal_type,
        "ui_type": proposal_type,
        "proposed_by_party": proposed_by_party,
        "candidate_party": candidate_party,
        "effects": {},
    }

    if proposal_type in ["policy", "region_policy"]:
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

    if proposal_type == "region_policy":
        proposal["region_policy"] = region_policy_data
        proposal["map_output"] = {
            "law_id": bill_id,
            "title": title,
            "passed": None,
            "actor": "Върховен Конгрес",
            "map_action_type": (
                "manual_regional_effect"
                if region_policy_data["policy_template"] == "manual_regional_effect"
                else "policy_template"
            ),
            "target_region": region_policy_data["target_region"],
            "target_problem": region_policy_data["target_problem"],
            "target_indicator": region_policy_data["target_indicator"],
            "policy_template": {
                "key": region_policy_data["policy_template"],
                "label": region_policy_data["policy_template_label"],
            },
            "scope": region_policy_data["scope"],
            "target_regions": [region_policy_data["target_region"]],
            "fiscal": {
                "amount_millions": region_policy_data["fiscal_amount_millions"],
                "amount_meaning": region_policy_data["fiscal_amount_meaning"],
                "funding_source": region_policy_data["funding_source"],
            },
            "expected_regional_effects": region_policy_data["expected_regional_effects"],
            "map_inputs": {
                "section": region_policy_data["recommended_map_section"],
                "law_id": bill_id,
                "template_label": region_policy_data["policy_template_label"],
                "scope": region_policy_data["scope"],
                "target_region": region_policy_data["target_region"],
                "cost_millions": region_policy_data["fiscal_amount_millions"],
                "funding_source": region_policy_data["funding_source"],
            },
            "risk_notes": [
                "Ефектите трябва да бъдат въведени ръчно в Political Economy Map Simulator.",
                "Регионално насочените политики могат да бъдат възприети като фаворизиране на една област.",
                "Фискалният ефект зависи от избрания източник на финансиране.",
            ],
        }

    st.write(f"Необходими гласове за приемане: {pass_threshold} от {TOTAL_SEATS}")

    progress_text = st.empty()
    progress_bar = st.progress(0)


    def update_progress(current_step, total_steps):
        progress_text.write(f"Гласуване... {current_step}/{total_steps}")
        progress_bar.progress(min(current_step / total_steps, 1.0))

    if proposal_type in ["policy", "region_policy"]:
        if party_position_mode == "Автоматично":
            proposal["party_positions"] = calculate_party_positions(proposal)
            st.subheader("Автоматично изчислени партийни позиции")
        else:
            proposal["party_positions"] = manual_party_positions
            st.subheader("Ръчно зададени партийни позиции")

        for party, position in proposal["party_positions"].items():
            st.write(f"{party}: {position}")
    else:
        proposal["party_positions"] = {}

    simulation_output = get_representative_vote(
        bots,
        proposal,
        n_runs=100,
        pass_threshold=pass_threshold,
        progress_callback=update_progress
    )

    results = simulation_output["results"]
    totals = simulation_output["totals"]
    party_totals = simulation_output["party_totals"]
    bill_passed = simulation_output["bill_passed"]

    progress_text.write(f"Гласуването приключи: {len(bots)}/{TOTAL_SEATS}")
    progress_bar.progress(1.0)

    st.subheader("Резултат")
    st.write(f"ЗА: {totals['YES']}")
    st.write(f"ПРОТИВ: {totals['NO']}")
    st.write(f"ВЪЗДЪРЖАЛ СЕ: {totals['ABSTAIN']}")

    if bill_passed:
        st.success("Законопроектът е ПРИЕТ")
    else:
        st.error("Законопроектът НЕ Е ПРИЕТ")

    if proposal_type == "region_policy":
        proposal["map_output"]["passed"] = bill_passed

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

    n_cols = 15
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

    st.session_state.last_vote_output = {
        "proposal": proposal,
        "results": results,
        "totals": totals,
        "party_totals": party_totals,
        "bill_passed": bill_passed,
        "region_policy_data": region_policy_data if proposal_type == "region_policy" else None,
        "proposal_type": proposal_type,
    }

    with open("parliament_report.pdf", "rb") as pdf_file:
        st.download_button(
            label="Изтегли PDF доклада",
            data=pdf_file.read(),
            file_name="parliament_report.pdf",
            mime="application/pdf",
            key="download_parliament_report_pdf"
        )

if st.session_state.last_vote_output:
    saved_output = st.session_state.last_vote_output
    saved_proposal = saved_output["proposal"]
    saved_region_policy_data = saved_output["region_policy_data"]
    saved_proposal_type = saved_output["proposal_type"]

    if saved_proposal_type == "region_policy" and saved_region_policy_data:
        st.divider()
        st.subheader("Практическа карта за Political Economy Map Simulator")

        map_output = saved_proposal["map_output"]

        st.write(f"**Law ID:** {map_output['law_id']}")
        st.write(f"**Заглавие:** {map_output['title']}")
        st.write(f"**Приет:** {'Да' if map_output['passed'] else 'Не'}")
        st.write(f"**Целева област:** {map_output['target_region']}")
        st.write(f"**Целеви показател:** {saved_region_policy_data['target_indicator_label']} ({map_output['target_indicator']})")
        st.write(f"**Секция в Map Simulator:** {map_output['map_inputs']['section']}")
        st.write(f"**Цена в млн.:** {map_output['fiscal']['amount_millions']}")
        st.write(f"**Финансиране:** {map_output['fiscal']['funding_source']}")

        if map_output["map_action_type"] == "manual_regional_effect":
            manual_change = list(saved_region_policy_data["expected_regional_effects"].values())[0]
            practical_text = f"""REGION-SPECIFIC POLICY EFFECTS CARD

Law ID: {map_output['law_id']}
Law title: {map_output['title']}
Passed: {map_output['passed']}
Target region: {map_output['target_region']}
Target problem: {map_output['target_problem']}
Target indicator: {map_output['target_indicator']} / {saved_region_policy_data['target_indicator_label']}
Recommended map section: Прилагане на решение

MAP SIMULATOR INPUTS:
Use section: Прилагане на решение
Decision title: {map_output['title']}
Target region: {map_output['target_region']}
Indicator: {saved_region_policy_data['target_indicator_label']}
Change: {manual_change}
Cost: {map_output['fiscal']['amount_millions']}
Funding source: {map_output['fiscal']['funding_source']}
"""
        else:
            practical_text = f"""REGION-SPECIFIC POLICY EFFECTS CARD

Law ID: {map_output['law_id']}
Law title: {map_output['title']}
Passed: {map_output['passed']}
Target region: {map_output['target_region']}
Target problem: {map_output['target_problem']}
Target indicator: {map_output['target_indicator']} / {saved_region_policy_data['target_indicator_label']}
Recommended map section: Прилагане на политически шаблон
Policy template: {map_output['policy_template']['key']} / {map_output['policy_template']['label']}
Scope: {map_output['scope']}
Cost in millions: {map_output['fiscal']['amount_millions']}
Funding source: {map_output['fiscal']['funding_source']}

MAP SIMULATOR INPUTS:
Use section: Прилагане на политически шаблон
Template: {map_output['policy_template']['label']}
Scope: {map_output['scope']}
Region: {map_output['target_region']}
Law ID: {map_output['law_id']}
Cost: {map_output['fiscal']['amount_millions']}
Funding source: {map_output['fiscal']['funding_source']}
"""

        st.markdown("**Готов текст за копиране:**")
        st.code(practical_text, language="text")

        import json

        download_col1, download_col2 = st.columns(2)
        with download_col1:
            st.download_button(
                label="Изтегли Policy Effects Card (.txt)",
                data=practical_text.encode("utf-8"),
                file_name=f"{map_output['law_id'] or 'policy_effects_card'}.txt",
                mime="text/plain",
                key="download_policy_effects_txt"
            )
        with download_col2:
            st.download_button(
                label="Изтегли Map JSON (.json)",
                data=json.dumps(map_output, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name=f"{map_output['law_id'] or 'map_output'}.json",
                mime="application/json",
                key="download_policy_effects_json"
            )

        with st.expander("Покажи copy-paste JSON"):
            st.json(map_output)
