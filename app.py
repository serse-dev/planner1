import streamlit as st
import pandas as pd
import os
import re

csv_path = "lesson_planner/csv_exports/Plan.csv"
shalg_path = "lesson_planner/csv_exports/Шалгуур.csv"
criteria_path = "lesson_planner/csv_exports/Үр дүнгийн шалгуур.csv"
level_path = "lesson_planner/csv_exports/Гүйцэтгэлийн түвшин.csv"

st.set_page_config(page_title="Ээлжит хичээлийн төлөвлөлт", page_icon="📚", layout="wide")

st.title("📚 Ээлжит хичээлийн төлөвлөлт")
st.markdown("""
<style>
.card {
    background-color: #f9f9fc;
    border-radius: 10px;
    padding: 1.5em;
    margin-bottom: 1em;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.header {
    font-size: 1.2em;
    font-weight: bold;
    color: #3a3a7c;
}
.goal {
    background-color: #eaf6ff;
    border-radius: 8px;
    padding: 1em;
    margin-top: 0.5em;
    font-size: 1.1em;
}
.shalg {
    background-color: #e6fff2;
    border-radius: 8px;
    padding: 1em;
    margin-top: 0.5em;
    font-size: 1.05em;
}
.outcome {
    background-color: #fff0e6;
    border-radius: 8px;
    padding: 1em;
    margin-top: 0.5em;
    font-size: 1.05em;
}
.copy-box {
    background-color: #f0f0ff;
    border-radius: 8px;
    padding: 1em;
    margin-top: 1em;
    font-size: 1em;
    border: 1px dashed #3a3a7c;
}
</style>
""", unsafe_allow_html=True)

def split_sentences(text):
    # . тэмдэглэгээгээр өгүүлбэр бүрийг мөр болгон хуваах
    if not isinstance(text, str):
        return []
    sentences = [s.strip() for s in re.split(r"\.(?!\d)", text) if s.strip()]
    sentences = [s + "." if not s.endswith(".") else s for s in sentences]
    # 1.1. 1.2 гэх мэт зөвхөн дугаарласан хоосон мөрийг хасна
    filtered = [s for s in sentences if not re.match(r"^\d+\.\d+\.*$", s)]
    return filtered

if not os.path.exists(csv_path):
    st.error(f"{csv_path} файл олдсонгүй.")
else:
    df = pd.read_csv(csv_path)
    df = df.rename(columns={
        "Судлагдахууны нэр": "Хичээлийн нэр",
        "Нэгжийн нэр": "Нэгж хичээл",
        "Ээлжит хичээл": "Ээлжит хичээл",
        "Ээлжит хичээлийн зорилго": "Ээлжит хичээлийн зорилго"
    })

    subjects = df["Хичээлийн нэр"].unique()
    subject = st.selectbox("Хичээлийн нэр сонгох", subjects)
    unit_df = df[df["Хичээлийн нэр"] == subject]
    units = unit_df["Нэгж хичээл"].unique()
    unit = st.selectbox("Нэгж хичээл сонгох", units)
    lesson_df = unit_df[unit_df["Нэгж хичээл"] == unit]
    lessons = lesson_df["Ээлжит хичээл"].unique()
    lesson = st.selectbox("Ээлжит хичээл сонгох", lessons)
    selected = lesson_df[lesson_df["Ээлжит хичээл"] == lesson]
    if selected.empty:
        st.warning("Тохирох ээлжит хичээл олдсонгүй.")
    else:
        selected = selected.iloc[0]

        # Шалгуур.csv файлаас тухайн ээлжит хичээлд тохирох суралцахуйн зорилт, үр дүн
        learning_objective = "Хоосон байна."
        learning_outcome = "Хоосон байна."
        objectives_list = []
        outcomes_list = []
        if os.path.exists(shalg_path):
            shalg_df = pd.read_csv(shalg_path)
            shalg_match = shalg_df[shalg_df["Ээлжит хичээл"] == lesson]
            if not shalg_match.empty:
                objectives_list = shalg_match["Суралцахуйн зорилт"].dropna().unique().tolist()
                outcomes_list = shalg_match["Суралцахуйн үр дүн"].dropna().unique().tolist()
                learning_objective = "<br>".join(objectives_list) if objectives_list else "Хоосон байна."
                learning_outcome = "<br>".join(outcomes_list) if outcomes_list else "Хоосон байна."
        else:
            learning_objective = "Шалгуур.csv файл олдсонгүй."
            learning_outcome = "Шалгуур.csv файл олдсонгүй."
            objectives_list = []
            outcomes_list = []

        st.markdown(f"""
        <div class="card">
            <div class="header">Хичээлийн нэр:</div>
            <div>{selected['Хичээлийн нэр']}</div>
            <div class="header">Нэгж хичээл:</div>
            <div>{selected['Нэгж хичээл']}</div>
            <div class="header">Ээлжит хичээл:</div>
            <div>{selected['Ээлжит хичээл']}</div>
            <div class="header">Суралцахуйн зорилт:</div>
            <div class="shalg">{learning_objective if learning_objective else "Хоосон байна."}</div>
            <div class="header">Ээлжит хичээлийн зорилго:</div>
            <div class="goal">{selected['Ээлжит хичээлийн зорилго'] if selected['Ээлжит хичээлийн зорилго'] else "Хоосон байна."}</div>
            <div class="header">Суралцахуйн үр дүн:</div>
            <div class="outcome">{learning_outcome if learning_outcome else "Хоосон байна."}</div>
        </div>
        """, unsafe_allow_html=True)

        # Үр дүнгийн шалгуур.csv-ээс харгалзах үр дүнгийн шалгуурыг авах
        result_df = None
        shown_shalguur_ids = set()
        if os.path.exists(criteria_path) and objectives_list:
            criteria_df = pd.read_csv(criteria_path)
            result_rows = []
            for obj in objectives_list:
                matched = criteria_df[criteria_df["Суралцахуйн зорилт"].astype(str).str.strip() == obj.strip()]
                for _, row in matched.iterrows():
                    outcome_criteria = row.get("Суралцахуйн үр  дүнгийн шалгуур", "Хоосон байна.")
                    for sentence in split_sentences(outcome_criteria):
                        result_rows.append({
                            "Суралцахуйн үр дүн": "",  # Суралцахуйн үр дүнг Шалгуур.csv-ээс outcomes_list-аас авна
                            "Суралцахуйн үр дүнгийн шалгуур": sentence,
                            "OUTCOMES CRITERIA ID": row.get("OUTCOMES CRITERIA ID", "")
                        })
            # outcomes_list-ийг үр дүн баганад харгалзуулж харуулна
            if result_rows and outcomes_list:
                max_len = max(len(outcomes_list), len(result_rows))
                outcomes_list += [""] * (max_len - len(outcomes_list))
                result_rows += [{"Суралцахуйн үр дүн": "", "Суралцахуйн үр дүнгийн шалгуур": "", "OUTCOMES CRITERIA ID": ""}] * (max_len - len(result_rows))
                for i in range(max_len):
                    result_rows[i]["Суралцахуйн үр дүн"] = outcomes_list[i]
                result_df = pd.DataFrame(result_rows)
                st.subheader("🎯 Суралцахуйн үр дүн, Суралцахуйн үр дүнгийн шалгуур")
                st.dataframe(result_df[["Суралцахуйн үр дүн", "Суралцахуйн үр дүнгийн шалгуур"]], use_container_width=True, hide_index=True)
            else:
                st.info("Суралцахуйн үр дүн эсвэл шалгуур олдсонгүй.")
        else:
            st.info("Үр дүнгийн шалгуур.csv файл эсвэл суралцахуйн зорилт олдсонгүй.")

        # Гүйцэтгэлийн түвшин.csv-ээс харгалзах шалгуурын түвшингүүдийг авах (давхардалгүйгээр)
        level_data = []
        if os.path.exists(level_path) and result_df is not None and not result_df.empty:
            level_df = pd.read_csv(level_path)
            for shalguur_id in result_df["OUTCOMES CRITERIA ID"].unique():
                if shalguur_id in shown_shalguur_ids or not shalguur_id:
                    continue
                shown_shalguur_ids.add(shalguur_id)
                level_match = level_df[level_df["Shalguur ID"].astype(str).str.strip() == str(shalguur_id).strip()]
                if not level_match.empty:
                    st.markdown(f"**Гүйцэтгэлийн түвшин ({shalguur_id}):**")
                    level_row = level_match.iloc[0]
                    levels = [
                        level_row.get("ГҮйцэтгэлийн I түвшин", "Хоосон байна."),
                        level_row.get("ГҮйцэтгэлийн II түвшин", "Хоосон байна."),
                        level_row.get("ГҮйцэтгэлийн III түвшин", "Хоосон байна."),
                        level_row.get("ГҮйцэтгэлийн IV түвшин", "Хоосон байна.")
                    ]
                    level_table = pd.DataFrame({
                        "I түвшин": split_sentences(levels[0]),
                        "II түвшин": split_sentences(levels[1]),
                        "III түвшин": split_sentences(levels[2]),
                        "IV түвшин": split_sentences(levels[3])
                    })
                    st.dataframe(level_table, use_container_width=True, hide_index=True)
                    # Промтод харуулах зорилгоор түвшний өгөгдлийг цуглуулна
                    level_data.append({
                        "id": shalguur_id,
                        "I": split_sentences(levels[0]),
                        "II": split_sentences(levels[1]),
                        "III": split_sentences(levels[2]),
                        "IV": split_sentences(levels[3])
                    })
                else:
                    st.info(f"{shalguur_id if shalguur_id else 'Хоосон байна.'} -д харгалзах гүйцэтгэлийн түвшин олдсонгүй.")
        elif os.path.exists(level_path):
            st.info("Гүйцэтгэлийн түвшин харуулах шалгуур олдсонгүй.")
        else:
            st.info("Гүйцэтгэлийн түвшин.csv файл олдсонгүй.")

        # --- Prompt үүсгэх хэсэг ---
        st.markdown("#### 📋 Prompt үүсгэх")
        # Гүйцэтгэлийн түвшний хүснэгтийг промтод оруулах
        level_text = ""
        if level_data:
            for l in level_data:
                level_text += f"\nГүйцэтгэлийн түвшин ({l['id']}):\n"
                level_text += f"I түвшин: {'; '.join(l['I'])}\n"
                level_text += f"II түвшин: {'; '.join(l['II'])}\n"
                level_text += f"III түвшин: {'; '.join(l['III'])}\n"
                level_text += f"IV түвшин: {'; '.join(l['IV'])}\n"

        default_prompt = f"""
Та дараах мэдээлэл дээр тулгуурлан ээлжит хичээлийн дэлгэрэнгүй төлөвлөлт гарга:
- Хичээлийн нэр: {selected['Хичээлийн нэр']}
- Нэгж хичээл: {selected['Нэгж хичээл']}
- Ээлжит хичээл: {selected['Ээлжит хичээл']}
- Суралцахуйн зорилт: {learning_objective}
- Ээлжит хичээлийн зорилго: {selected['Ээлжит хичээлийн зорилго']}
- Суралцахуйн үр дүн: {learning_outcome}

Төлөвлөлтийн загвар:
1. Хичээлийн үе шат (Хугацаа, Багшийн үйл ажиллагаа, Сурагчийн үйл ажиллагаа гэсэн баганатай хүснэгт)
2. Үнэлгээний нэгж, шалгуур
3. Дасгал, бодлого, даалгавар (Хичээлийн үе шат бүрд даалгавар оруулахдаа Суралцахуйн үр дүн, суралцахуйн үр дүнгийн шалгуурт баримжаалан, гүйцэтгэлийн 4 түвшний шалгуурт тулгуурлан 5 хүртэлх даалгавар боловсруулна уу. 4 түвшний шалгуур болон суралцахуйн үр дүнг сонгогдсон ээлжит хичээлтэй уялдуулан гаргаж өгнө.)
4. Дүгнэлт, гэрийн даалгавар
5. Хичээлийн үе шат бүрд 5 хүртэлх дасгал, бодлого, даалгавар оруулна уу. Дасгал бүрийг дараах байдлаар тодорхойлно:

{level_text}
"""
        extra_text = st.text_area("Промтод нэмэх зүйлээ бичнэ үү", key="extra_prompt")
        prompt_full = default_prompt.strip() + "\n" + extra_text.strip() if extra_text else default_prompt.strip()

        if st.button("Промт үүсгэх", key="make_prompt_btn"):
            st.session_state['show_prompt_copy'] = True

        if st.session_state.get('show_prompt_copy', False):
            st.markdown(f"""
            <div class="copy-box">
            <b>Prompt:</b><br>
            <pre>{prompt_full}</pre>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("**Prompt-ыг COPY хийж дараах талбарт оруулна уу.**")
            if st.button("COPY", key="copy_btn"):
                st.session_state['show_prompt_copy'] = False
                st.session_state['show_plan_input'] = True

        if st.session_state.get('show_plan_input', False):
            st.markdown("#### 📝 Prompt-оор үүсгэсэн төлөвлөлтөө энд paste хийнэ үү:")
            user_plan = st.text_area("Төлөвлөлтөө энд paste хийнэ үү", height=200, key="plan_paste")
            if st.button("Төлөвлөгөөг харах", key="show_plan_btn") and user_plan:
                tables = re.findall(r"((?:\|.*\|\n)+)", user_plan)
                if tables:
                    for table in tables:
                        lines = [line.strip() for line in table.strip().split("\n") if line.strip()]
                        headers = []
                        data_rows = []
                        for i, line in enumerate(lines):
                            cols = [c.strip() for c in line.split("|") if c.strip()]
                            if i == 0:
                                headers = cols
                            elif len(cols) == len(headers):
                                data_rows.append(cols)
                        if headers and data_rows:
                            df_plan = pd.DataFrame(data_rows, columns=headers)
                            st.dataframe(df_plan, use_container_width=True, hide_index=True)
                        else:
                            st.markdown(f'<div class="copy-box">{table}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="copy-box">{user_plan}</div>', unsafe_allow_html=True)
                st.session_state['show_plan_input'] = False

        # Default хичээлийн үе шат
        lesson_stages = [
            {
                "Хугацаа": "5 мин",
                "Багшийн үйл ажиллагаа": "Сэдэв танилцуулах, анхаарал төвлөрүүлэх",
                "Сурагчийн үйл ажиллагаа": "Анхааралтай сонсох, асуултад хариулах"
            },
            {
                "Хугацаа": "15 мин",
                "Багшийн үйл ажиллагаа": "Шинэ мэдлэг тайлбарлах, жишээ үзүүлэх",
                "Сурагчийн үйл ажиллагаа": "Жишээг дагаж хийх, асуулт асуух"
            },
            {
                "Хугацаа": "15 мин",
                "Багшийн үйл ажиллагаа": "Дасгал ажил өгөх, хянах",
                "Сурагчийн үйл ажиллагаа": "Дасгал бодох, багт ажиллах"
            },
            {
                "Хугацаа": "5 мин",
                "Багшийн үйл ажиллагаа": "Дүгнэлт хийх, гэрийн даалгавар өгөх",
                "Сурагчийн үйл ажиллагаа": "Дүгнэлт хэлэх, гэрийн даалгавар авах"
            }
        ]
        stages_df = pd.DataFrame(lesson_stages)
        st.subheader("📝 Хичээлийн үе шат бүрээр төлөвлөлт")
        st.dataframe(stages_df, use_container_width=True, hide_index=True)