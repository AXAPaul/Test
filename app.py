import os
import json
from datetime import datetime
from uuid import uuid4
import mimetypes

import streamlit as st


def safe_rerun():
    """Compatibilité Streamlit pour relancer le script proprement."""
    rerun_fn = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if callable(rerun_fn):
        rerun_fn()


# -----------------------------
# Configuration et constantes
# -----------------------------
APP_TITLE = "AXA | Plateforme Documents"
DATA_DIR = "data"
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def ensure_storage():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def delete_record(record_id: str) -> bool:
    """Supprime un enregistrement d'historique et le fichier associé."""
    history = load_history()
    index = next((i for i, r in enumerate(history) if r.get("id") == record_id), None)
    if index is None:
        return False
    rec = history.pop(index)
    # Tente de supprimer le fichier du disque
    file_path = rec.get("path")
    if file_path:
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
        except Exception:
            # On ignore les erreurs de suppression non critiques
            pass
    save_history(history)
    return True


def format_size(num_bytes: int) -> str:
    if num_bytes is None:
        return "-"
    step_unit = 1024.0
    units = ["octets", "Ko", "Mo", "Go", "To"]
    size = float(num_bytes)
    for unit in units:
        if size < step_unit:
            if unit == "octets":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"
        size /= step_unit
    return f"{size:.2f} Po"


def store_uploaded_file(uploaded_file):
    """Sauvegarde le fichier et renvoie un enregistrement d'historique."""
    ensure_storage()

    original_name = os.path.basename(uploaded_file.name)
    content = uploaded_file.getvalue()
    size_bytes = len(content)
    mime, _ = mimetypes.guess_type(original_name)
    mime = mime or "application/octet-stream"

    # Préfixer pour éviter les collisions et assainir le chemin
    unique_id = uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stored_name = f"{timestamp}_{unique_id}_{original_name}"
    stored_path = os.path.join(UPLOADS_DIR, stored_name)

    with open(stored_path, "wb") as f:
        f.write(content)

    record = {
        "id": unique_id,
        "original_name": original_name,
        "stored_name": stored_name,
        "path": stored_path,
        "size_bytes": size_bytes,
        "mime": mime,
        "uploaded_at": datetime.now().isoformat(timespec="seconds"),
    }

    history = load_history()
    history.append(record)
    save_history(history)

    return record


def render_header():
    st.markdown(
        "<style> .nav-btn {margin-right: 0.5rem;} .page-info{color:#6c757d;} </style>",
        unsafe_allow_html=True,
    )
    st.title(APP_TITLE)
    cols = st.columns([1, 1, 6])
    with cols[0]:
        try:
            clicked_upload = st.button(
                "Uploader", key="nav_upload", help="Aller à l'upload", type="primary"
            )
        except TypeError:
            clicked_upload = st.button("Uploader", key="nav_upload", help="Aller à l'upload")
    with cols[1]:
        try:
            clicked_history = st.button(
                "Historique", key="nav_history", help="Voir l'historique", type="secondary"
            )
        except TypeError:
            clicked_history = st.button("Historique", key="nav_history", help="Voir l'historique")

    if clicked_upload:
        st.session_state["page"] = "upload"
        safe_rerun()
    if clicked_history:
        st.session_state["page"] = "history"
        safe_rerun()

    current = st.session_state.get("page", "upload")
    st.caption(f"Page actuelle : {'Téléversement' if current == 'upload' else 'Historique'}")
    st.divider()


def page_upload():
    st.subheader("Téléverser un document")
    st.write("Sélectionnez un fichier depuis votre machine (repo local).")

    uploaded_file = st.file_uploader(
        "Choisir un fichier",
        type=None,
        accept_multiple_files=False,
    )

    if uploaded_file is not None:
        with st.spinner("Sauvegarde en cours..."):
            record = store_uploaded_file(uploaded_file)
            st.session_state["last_upload"] = record

        st.success(
            f"Fichier '{record['original_name']}' téléversé avec succès (" +
            f"{format_size(record['size_bytes'])})."
        )

    # Zone d'action après un upload
    last = st.session_state.get("last_upload")
    if last:
        col1, col2 = st.columns([1, 1])
        with col1:
            try:
                with open(last["path"], "rb") as f:
                    st.download_button(
                        label=f"Télécharger {last['original_name']}",
                        data=f.read(),
                        file_name=last["original_name"],
                        mime=last["mime"],
                        key=f"dl_last_{last['id']}"
                    )
            except FileNotFoundError:
                st.error("Fichier introuvable sur le serveur.")
        with col2:
            if st.button("Aller à l'historique"):
                st.session_state["page"] = "history"
                safe_rerun()

    st.info(
        "Formats acceptés: tout type de fichier. Les documents sont stockés "
        "localement dans le dossier 'data/uploads/'."
    )


def page_history():
    st.subheader("Historique des documents envoyés")
    ensure_storage()
    history = load_history()

    if not history:
        st.info("Aucun document n'a encore été téléversé.")
        return

    # Tri décroissant par date
    history_sorted = sorted(history, key=lambda r: r.get("uploaded_at", ""), reverse=True)

    # Statistiques rapides
    last_dt = history_sorted[0].get("uploaded_at")
    total_size = sum(r.get("size_bytes", 0) for r in history_sorted)
    c1, c2, c3 = st.columns(3)
    c1.metric("Documents", f"{len(history_sorted)}")
    c2.metric("Dernier téléversement", last_dt or "-")
    c3.metric("Espace utilisé", format_size(total_size))

    # Tableau synthétique
    table = [
        {
            "Date": r.get("uploaded_at", "-"),
            "Fichier": r.get("original_name", "-"),
            "Taille": format_size(r.get("size_bytes")),
            "Type": r.get("mime", "-"),
        }
        for r in history_sorted
    ]

    # Affichage tableau
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.divider()
    st.write("Téléchargements")
    for r in history_sorted:
        file_path = r.get("path")
        file_label = f"{r.get('original_name')} ({format_size(r.get('size_bytes'))})"
        cols = st.columns([5, 1, 1])
        cols[0].write(f"• {file_label}")
        try:
            with open(file_path, "rb") as f:
                cols[1].download_button(
                    label="Télécharger",
                    data=f.read(),
                    file_name=r.get("original_name"),
                    mime=r.get("mime"),
                    key=f"dl_{r.get('id')}"
                )
        except FileNotFoundError:
            cols[1].error("Manquant")

        if cols[2].button("Supprimer", key=f"del_{r.get('id')}"):
            if delete_record(r.get("id")):
                st.success(f"Supprimé: {r.get('original_name')}")
                safe_rerun()


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="📄", layout="wide")
    if "page" not in st.session_state:
        st.session_state["page"] = "upload"

    render_header()

    page = st.session_state.get("page", "upload")
    if page == "upload":
        page_upload()
    else:
        page_history()


if __name__ == "__main__":
    ensure_storage()
    main()
