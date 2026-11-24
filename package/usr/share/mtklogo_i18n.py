"""
Lightweight translation for the mtklogo GUI (without gettext/lrelease).

* The source text is ENGLISH: if there is no translation, it appears in English.
* Detected language (in this order): MTKLOGO_GUI_LANG, LANGUAGE, LC_ALL, LC_MESSAGES,
  LANG and, finally, the system language according to Qt. Ex.: MTKLOGO_GUI_LANG=de ./app
* Built-in catalogs: pt, de, es, fr, ru.
* To ADD a language without recompiling: create ~/mtklogo-gui/lang/<code>.json
  with {"English text": "translation", ...} (copy the CATALOG["de"] keys below).
  The same applies to script v2: ~/mtklogo-gui/lang/<code>.sh (see suggested /lang/).
*  Catalog was rebuild with mtklogo_gui v1.3; v1.4 and updated in v1.5
"""
from __future__ import annotations
    
import json
import os
from pathlib import Path

CATALOG: dict[str, dict[str, str]] = {
    "pt": {
        "Original mtklogo source code binary": "Código-fonte e binário originais do mtklogo",
        "Upstream source code binary v1.0.1; improvements and ideas in yaml file": "Código-fonte e binário upstream v1.0.1; melhorias e ideias no arquivo yaml",
        "Upstream source code binary v1.1; update, improvements and ideas in yaml file; update source code to the new logo.bin files - Multi-image; Creator and designer of the GUI for mtklogo": "Código-fonte e binário upstream v1.1; atualização, melhorias e ideias no arquivo yaml; atualização do código-fonte para os novos arquivos logo.bin - Multi-imagem; criador e designer do GUI do mtklogo",
        "OK": "OK",
        "Cancel": "Cancelar",
        "1 image": "1 imagem",
        "{n} images": "{n} imagens",
        "Authors": "Autores",
        "Close": "Fechar",
        "Folder…": "Pasta…",
        "Open": "Abrir",
        "Choose logo.bin…": "Escolher logo.bin…",
        "▶  Run mtklogos.sh": "▶  Executar mtklogos.sh",
        "■  Stop": "■  Parar",
        "Press “Run mtklogos.sh” to start.": "Pressione « Executar mtklogos.sh » para começar.",
        "Save log": "Salvar Log",
        "Quit": "Sair",
        "Ready.": "Pronto.",
        "Folder with mtklogos.sh, mtklogo and logo.bin": "Pasta com mtklogos.sh, mtklogo e logo.bin",
        "Choose your logo.bin": "Escolha o seu logo.bin",
        "Logo images (*.bin);;All files (*)": "Imagens de logo (*.bin);;Todos os arquivos (*)",
        "logo.bin copied to {path}": "logo.bin copiado para {path}",
        "Log saved to {path}": "Log salvo em {path}",
        "Running…": "Executando…",
        "Running {script} (PID {pid})…": "Executando {script} (PID {pid})…",
        "Stopping the script…": "Encerrando o script…",
        "— Script finished (exit code {code}) —": "— Script finalizado (código de saída {code}) —",
        "Finished (code {code}).": "Finalizado (código {code}).",
        "Waiting for your answer…": "Aguardando sua resposta…",
        "Select an option:": "Selecione uma opção:",
        "Cancel?": "Cancelar?",
        "Cancelling stops the script.\nDo you really want to stop the running process?": "Cancelar encerra o script.\nDeseja realmente parar a execução?",
        "The script asks for a value": "O script pede um valor",
        "Script confirmation": "Confirmação do script",
        "The script is waiting": "O script aguarda",
        "Continue": "Continuar",
        "Warning: this program was made for Linux.": "Aviso: este programa foi feito para Linux.",
        "No images here yet.\nRun “Unpack logo.bin” to extract them.": "Ainda não há imagens aqui.\nExecute 'Descompactar logo.bin' para extraí-las.",
        "Replace logo.bin?": "Substituir logo.bin?",
        "A logo.bin already exists in:\n{path}\n\nReplace it with the selected file?\n(the original, if already used by the script, is kept in backup/)": "Já existe um logo.bin em:\n{path}\n\nSubstituir pelo arquivo escolhido?\n(o original, se já usado pelo script, fica guardado em backup/)",
        "Nothing to save yet.": "Ainda não há nada para salvar.",
        "Script not found": "Script não encontrado",
        "{script} does not exist in:\n{path}\n\nUse “Folder…” to choose the correct folder.": "{script} não existe em:\n{path}\n\nUse “Pasta…” para escolher a pasta correta.",
        "Input:": "Entrada:",
        "Script running": "Script em execução",
        "The script is still running. Stop it and quit?": "O script ainda está rodando. Encerrar e sair?",
        "Copy error": "Erro ao copiar",
        "Could not save the log:\n{error}": "Não foi possível salvar o log:\n{error}",
        "Start error": "Erro ao iniciar",
        "The script asks for the number of an option:": "O script pede o número de uma opção:",
        "Failed to send: the script is no longer reading input.": "Falha ao enviar: o script não está mais lendo a entrada.",
        "The script is waiting for input:": "O script está aguardando uma entrada:",
        "Folder not found: {path}": "Pasta não encontrada: {path}",
        "The script asks for a choice": "Confirme sua escolha",
        "No image for '{name}'.": "Sem imagens em '{name}'.",
        "{n} image(s) found for '{name}'.": "{n} imagen(s) encontrada(s) em '{name}'."
    },
    "de": {
        "Original mtklogo source code binary": "Original-Quellcode und Binärdatei von mtklogo",
        "Upstream source code binary v1.0.1; improvements and ideas in yaml file": "Upstream-Quellcode und Binärdatei v1.0.1; Verbesserungen und Ideen in der yaml-Datei",
        "Upstream source code binary v1.1; update, improvements and ideas in yaml file; update source code to the new logo.bin files - Multi-image; Creator and designer of the GUI for mtklogo": "Upstream-Quellcode und Binärdatei v1.1; Aktualisierung, Verbesserungen und Ideen in der yaml-Datei; Quellcode für die neuen logo.bin-Dateien aktualisiert - Multi-Image; Entwickler und Designer der GUI für mtklogo",
        "OK": "OK",
        "Cancel": "Abbrechen",
        "1 image": "1 Bild",
        "{n} images": "{n} Bilder",
        "Authors": "Autoren",
        "Close": "Schließen",
        "Folder…": "Ordner…",
        "Open": "Öffnen",
        "Choose logo.bin…": "logo.bin wählen…",
        "▶  Run mtklogos.sh": "▶  mtklogos.sh ausführen",
        "■  Stop": "■  Stopp",
        "Press “Run mtklogos.sh” to start.": "Zum Starten auf « mtklogos.sh ausführen » klicken.",
        "Save log": "Log speichern",
        "Quit": "Beenden",
        "Ready.": "Bereit.",
        "Folder with mtklogos.sh, mtklogo and logo.bin": "Ordner mit mtklogos.sh, mtklogo und logo.bin",
        "Choose your logo.bin": "Wählen Sie Ihre logo.bin",
        "Logo images (*.bin);;All files (*)": "Logo-Images (*.bin);;Alle Dateien (*)",
        "logo.bin copied to {path}": "logo.bin nach {path} kopiert",
        "Log saved to {path}": "Log gespeichert unter {path}",
        "Running…": "Läuft…",
        "Running {script} (PID {pid})…": "{script} läuft (PID {pid})…",
        "Stopping the script…": "Skript wird beendet…",
        "— Script finished (exit code {code}) —": "— Skript beendet (Exit-Code {code}) —",
        "Finished (code {code}).": "Beendet (Code {code}).",
        "Waiting for your answer…": "Warte auf Ihre Antwort…",
        "Select an option:": "Wählen Sie eine Option:",
        "Cancel?": "Abbrechen?",
        "Cancelling stops the script.\nDo you really want to stop the running process?": "Abbrechen beendet das Skript.\nWollen Sie die Ausführung wirklich stoppen?",
        "The script asks for a value": "Das Skript verlangt einen Wert",
        "Script confirmation": "Bestätigung des Skripts",
        "The script is waiting": "Das Skript wartet",
        "Continue": "Weiter",
        "Warning: this program was made for Linux.": "Warnung: Dieses Programm wurde für Linux entwickelt.",
        "No images here yet.\nRun “Unpack logo.bin” to extract them.": "Hier gibt es noch keine Bilder.\nFühren Sie 'Auspacken logo.bin' aus, um sie zu extrahieren.",
        "Replace logo.bin?": "logo.bin ersetzen?",
        "A logo.bin already exists in:\n{path}\n\nReplace it with the selected file?\n(the original, if already used by the script, is kept in backup/)": "In diesem Ordner existiert bereits eine logo.bin:\n{path}\n\nMit der gewählten Datei ersetzen?\n(Das Original wird, falls vom Skript schon verwendet, in backup/ aufbewahrt)",
        "Nothing to save yet.": "Es gibt noch nichts zu speichern.",
        "Script not found": "Skript nicht gefunden",
        "{script} does not exist in:\n{path}\n\nUse “Folder…” to choose the correct folder.": "{script} existiert nicht in:\n{path}\n\nWählen Sie über „Ordner…“ den richtigen Ordner.",
        "Input:": "Eingabe:",
        "Script running": "Skript läuft",
        "The script is still running. Stop it and quit?": "Das Skript läuft noch. Beenden und schließen?",
        "Copy error": "Kopierfehler",
        "Could not save the log:\n{error}": "Das Log konnte nicht gespeichert werden:\n{error}",
        "Start error": "Startfehler",
        "The script asks for the number of an option:": "Das Skript fragt nach der Nummer einer Option:",
        "Failed to send: the script is no longer reading input.": "Senden fehlgeschlagen: Das Skript liest keine Eingabe mehr.",
        "The script is waiting for input:": "Das Skript wartet auf eine Eingabe:",
        "Folder not found: {path}": "Ordner nicht gefunden: {path}",
        "The script asks for a choice": "Bestätigen Sie Ihre Entscheidung",
        "No image for '{name}'.": "Keine Bilder in '{name}'.",
        "{n} image(s) found for '{name}'.": "{n} Bild(er) gefunden in '{name}'."
    },
    "es": {
        "Original mtklogo source code binary": "Código fuente y binario originales de mtklogo",
        "Upstream source code binary v1.0.1; improvements and ideas in yaml file": "Código fuente y binario upstream v1.0.1; mejoras e ideas en el archivo yaml",
        "Upstream source code binary v1.1; update, improvements and ideas in yaml file; update source code to the new logo.bin files - Multi-image; Creator and designer of the GUI for mtklogo": "Código fuente y binario upstream v1.1; actualización, mejoras e ideas en el archivo yaml; código fuente actualizado para los nuevos archivos logo.bin - Multi-imagen; creador y diseñador de la GUI de mtklogo",
        "OK": "Aceptar",
        "Cancel": "Cancelar",
        "1 image": "1 imagen",
        "{n} images": "{n} imágenes",
        "Authors": "Autores",
        "Close": "Cerrar",
        "Folder…": "Carpeta…",
        "Open": "Abrir",
        "Choose logo.bin…": "Elegir logo.bin…",
        "▶  Run mtklogos.sh": "▶  Ejecutar mtklogos.sh",
        "■  Stop": "■  Detener",
        "Press “Run mtklogos.sh” to start.": "Pulse « Ejecutar mtklogos.sh » para empezar.",
        "Save log": "Guardar log",
        "Quit": "Salir",
        "Ready.": "Listo.",
        "Folder with mtklogos.sh, mtklogo and logo.bin": "Carpeta con mtklogos.sh, mtklogo y logo.bin",
        "Choose your logo.bin": "Elija su logo.bin",
        "Logo images (*.bin);;All files (*)": "Imágenes de logo (*.bin);;Todos los archivos (*)",
        "logo.bin copied to {path}": "logo.bin copiado a {path}",
        "Log saved to {path}": "Log guardado en {path}",
        "Running…": "Ejecutando…",
        "Running {script} (PID {pid})…": "Ejecutando {script} (PID {pid})…",
        "Stopping the script…": "Deteniendo el script…",
        "— Script finished (exit code {code}) —": "— Script finalizado (código de salida {code}) —",
        "Finished (code {code}).": "Finalizado (código {code}).",
        "Waiting for your answer…": "Esperando su respuesta…",
        "Select an option:": "Seleccione una opción:",
        "Cancel?": "¿Cancelar?",
        "Cancelling stops the script.\nDo you really want to stop the running process?": "Cancelar detiene el script.\n¿Realmente desea detener la ejecución?",
        "The script asks for a value": "El script pide un valor",
        "Script confirmation": "Confirmación del script",
        "The script is waiting": "El script espera",
        "Continue": "Continuar",
        "Warning: this program was made for Linux.": "Aviso: este programa fue hecho para Linux.",
        "No images here yet.\nRun “Unpack logo.bin” to extract them.": "Todavía no hay imágenes aquí.\nEjecute 'Descomprime logo.bin' para extraerlas.",
        "Replace logo.bin?": "¿Reemplazar logo.bin?",
        "A logo.bin already exists in:\n{path}\n\nReplace it with the selected file?\n(the original, if already used by the script, is kept in backup/)": "Ya existe un logo.bin en:\n{path}\n\n¿Reemplazarlo por el archivo elegido?\n(el original, si el script ya lo usó, se conserva en backup/)",
        "Nothing to save yet.": "Todavía no hay nada que guardar.",
        "Script not found": "Script no encontrado",
        "{script} does not exist in:\n{path}\n\nUse “Folder…” to choose the correct folder.": "{script} no existe en:\n{path}\n\nUse «Carpeta…» para elegir la carpeta correcta.",
        "Input:": "Entrada:",
        "Script running": "Script en ejecución",
        "The script is still running. Stop it and quit?": "El script sigue en ejecución. ¿Detenerlo y salir?",
        "Copy error": "Error al copiar",
        "Could not save the log:\n{error}": "No se pudo guardar el log:\n{error}",
        "Start error": "Error al iniciar",
        "The script asks for the number of an option:": "El script pide el número de una opción:",
        "Failed to send: the script is no longer reading input.": "Error al enviar: el script ya no lee la entrada.",
        "The script is waiting for input:": "El script espera una entrada:",
        "Folder not found: {path}": "Carpeta no encontrada: {path}",
        "The script asks for a choice": "Confirma tu elección",
        "No image for '{name}'.": "No hay imágenes en '{name}'.",
        "{n} image(s) found for '{name}'.": "{n} imágen(es) encontrada(s) en '{name}'."
    },
    "fr": {
        "Original mtklogo source code binary": "Code source et binaire d’origine de mtklogo",
        "Upstream source code binary v1.0.1; improvements and ideas in yaml file": "Code source et binaire upstream v1.0.1 ; améliorations et idées dans le fichier yaml",
        "Upstream source code binary v1.1; update, improvements and ideas in yaml file; update source code to the new logo.bin files - Multi-image; Creator and designer of the GUI for mtklogo": "Code source et binaire upstream v1.1 ; mise à jour, améliorations et idées dans le fichier yaml ; code source mis à jour pour les nouveaux fichiers logo.bin - Multi-image ; créateur et concepteur de l’interface de mtklogo",
        "OK": "OK",
        "Cancel": "Annuler",
        "1 image": "1 image",
        "{n} images": "{n} images",
        "Authors": "Auteurs",
        "Close": "Fermer",
        "Folder…": "Dossier…",
        "Open": "Ouvrir",
        "Choose logo.bin…": "Choisir logo.bin…",
        "▶  Run mtklogos.sh": "▶  Lancer mtklogos.sh",
        "■  Stop": "■  Arrêter",
        "Press “Run mtklogos.sh” to start.": "Cliquez sur « Lancer mtklogos.sh » pour commencer.",
        "Save log": "Enregistrer le journal",
        "Quit": "Quitter",
        "Ready.": "Prêt.",
        "Folder with mtklogos.sh, mtklogo and logo.bin": "Dossier contenant mtklogos.sh, mtklogo et logo.bin",
        "Choose your logo.bin": "Choisissez votre logo.bin",
        "Logo images (*.bin);;All files (*)": "Images de logo (*.bin);;Tous les fichiers (*)",
        "logo.bin copied to {path}": "logo.bin copié vers {path}",
        "Log saved to {path}": "Journal enregistré dans {path}",
        "Running…": "En cours…",
        "Running {script} (PID {pid})…": "Exécution de {script} (PID {pid})…",
        "Stopping the script…": "Arrêt du script…",
        "— Script finished (exit code {code}) —": "— Script terminé (code de sortie {code}) —",
        "Finished (code {code}).": "Terminé (code {code}).",
        "Waiting for your answer…": "En attente de votre réponse…",
        "Select an option:": "Sélectionnez une option :",
        "Cancel?": "Annuler ?",
        "Cancelling stops the script.\nDo you really want to stop the running process?": "Annuler arrête le script.\nVoulez-vous vraiment arrêter l'exécution ?",
        "The script asks for a value": "Le script demande une valeur",
        "Script confirmation": "Confirmation du script",
        "The script is waiting": "Le script attend",
        "Continue": "Continuer",
        "Warning: this program was made for Linux.": "Attention : ce programme est conçu pour Linux.",
        "No images here yet.\nRun “Unpack logo.bin” to extract them.": "Aucune image pour l’instant.\nLancez 'Décompresser logo.bin' pour les extraire.",
        "Replace logo.bin?": "Remplacer logo.bin ?",
        "A logo.bin already exists in:\n{path}\n\nReplace it with the selected file?\n(the original, if already used by the script, is kept in backup/)": "Un logo.bin existe déjà dans :\n{path}\n\nLe remplacer par le fichier choisi ?\n(l'original, s'il a déjà servi au script, est conservé dans backup/)",
        "Nothing to save yet.": "Rien à enregistrer pour l’instant.",
        "Script not found": "Script introuvable",
        "{script} does not exist in:\n{path}\n\nUse “Folder…” to choose the correct folder.": "{script} n'existe pas dans :\n{path}\n\nUtilisez « Dossier… » pour choisir le bon dossier.",
        "Input:": "Saisie :",
        "Script running": "Script en cours",
        "The script is still running. Stop it and quit?": "Le script est toujours en cours. L'arrêter et quitter ?",
        "Copy error": "Erreur de copie",
        "Could not save the log:\n{error}": "Impossible d’enregistrer le journal :\n{error}",
        "Start error": "Erreur de démarrage",
        "The script asks for the number of an option:": "Le script demande le numéro d'une option :",
        "Failed to send: the script is no longer reading input.": "Échec de l'envoi : le script ne lit plus la saisie.",
        "The script is waiting for input:": "Le script attend une saisie :",
        "Folder not found: {path}": "Dossier introuvable: {path}",
        "The script asks for a choice": "Confirmez votre choix",
        "No image for '{name}'.": "Aucune image dans '{name}'.",
        "{n} image(s) found for '{name}'.": "{n} image(s) trouvée(s) dans '{name}'."
    },
    "ru": {
        "Original mtklogo source code binary": "Оригинальный исходный код и бинарный файл mtklogo",
        "Upstream source code binary v1.0.1; improvements and ideas in yaml file": "Исходный код и бинарный файл upstream v1.0.1; улучшения и идеи в файле yaml",
        "Upstream source code binary v1.1; update, improvements and ideas in yaml file; update source code to the new logo.bin files - Multi-image; Creator and designer of the GUI for mtklogo": "Исходный код и бинарный файл upstream v1.1; обновление, улучшения и идеи в файле yaml; исходный код обновлён для новых файлов logo.bin - Multi-image; автор и дизайнер GUI для mtklogo",
        "OK": "ОК",
        "Cancel": "Отмена",
        "1 image": "1 изображение",
        "{n} images": "изображений: {n}",
        "Authors": "Авторы",
        "Close": "Закрыть",
        "Folder…": "Папка…",
        "Open": "Открыть",
        "Choose logo.bin…": "Выберите logo.bin…",
        "▶  Run mtklogos.sh": "▶  Запустить mtklogos.sh",
        "■  Stop": "■  Стоп",
        "Press “Run mtklogos.sh” to start.": "Нажмите « Запустить mtklogos.sh », чтобы начать.",
        "Save log": "Сохранить лог",
        "Quit": "Выход",
        "Ready.": "Готово.",
        "Folder with mtklogos.sh, mtklogo and logo.bin": "Папка с mtklogos.sh , mtklogo и logo.bin",
        "Choose your logo.bin": "Выберите свой logo.bin",
        "Logo images (*.bin);;All files (*)": "Изображения логотипа (*.bin);;Все файлы (*)",
        "logo.bin copied to {path}": "logo.bin скопирован в {path}",
        "Log saved to {path}": "Лог сохранён: {path}",
        "Running…": "Пуск…",
        "Running {script} (PID {pid})…": "Запуск {script} (PID {pid})…",
        "Stopping the script…": "Закрытие скрипта…",
        "— Script finished (exit code {code}) —": "— Готовый скрипт (код завершения {code}) —",
        "Finished (code {code}).": "Завершено (код {code}).",
        "Waiting for your answer…": "Ожидание вашего ответа…",
        "Select an option:": "Выберите один из вариантов:",
        "Cancel?": "Отменить?",
        "Cancelling stops the script.\nDo you really want to stop the running process?": "Отмена завершает работу скрипта.\nТы действительно хочешь остановиться?",
        "The script asks for a value": "Скрипт запрашивает значение",
        "Script confirmation": "Подтверждение сценария",
        "The script is waiting": "Сценарий ожидает",
        "Continue": "Продолжать",
        "Warning: this program was made for Linux.": "Внимание: эта программа была создана для Linux.",
        "No images here yet.\nRun “Unpack logo.bin” to extract them.": "Здесь пока нет изображений.\nВыполните 'Распаковать logo.bin', чтобы извлечь их.",
        "Replace logo.bin?": "Заменить logo.bin?",
        "A logo.bin already exists in:\n{path}\n\nReplace it with the selected file?\n(the original, if already used by the script, is kept in backup/)": "Уже существует файл logo.bin:\n{path}\n\nЗаменить выбранным файлом?\n(исходный файл, если он уже используется скриптом, сохраняется в папке backup/)",
        "Nothing to save yet.": "Пока нечего сохранять.",
        "Script not found": "Скрипт не найден",
        "{script} does not exist in:\n{path}\n\nUse “Folder…” to choose the correct folder.": "{script} не существует в:\n{path}\n\nИспользуйте «Папка…», чтобы выбрать правильную папку.",
        "Input:": "Ввод:",
        "Script running": "Запущенный скрипт",
        "The script is still running. Stop it and quit?": "Сценарий все еще запущен. Закрыть все и выйти?",
        "Copy error": "Ошибка копирования",
        "Could not save the log:\n{error}": "Не удалось сохранить лог:\n{error}",
        "Start error": "Ошибка при запуске",
        "The script asks for the number of an option:": "Скрипт запрашивает номер опции:",
        "Failed to send: the script is no longer reading input.": "Не удалось отправить: скрипт больше не считывает вводимые данные.",
        "The script is waiting for input:": "Скрипт ожидает ввода данных:",
        "Folder not found: {path}": "Папка не найдена: {path}",
        "The script asks for a choice": "Подтвердите свой выбор",
        "No image for '{name}'.": "В картинах нет '{name}'.",
        "{n} image(s) found for '{name}'.": "{n} изображение(я) найдено(ы) на '{name}'."
    },
}

LANG = "en"        # base code in use (en, pt, de, es, fr, ru, ...)
LOCALE = "en_US"   # complete locale (used to load Qt translations)
_extra: dict[str, str] = {}


def _norm(value: str):
    """'pt_BR.UTF-8@x' -> ('pt', 'pt_BR'); 'C'/'POSIX' -> ('en','en_US')."""
    value = value.strip()
    if not value:
        return None
    if value in ("C", "POSIX"):
        return "en", "en_US"
    code = value.split(".")[0].split("@")[0].replace("-", "_")
    base = code.split("_")[0].lower()
    if not base.isalpha():
        return None
    return base, (code if "_" in code else base)


def available_languages(extra_dirs=()) -> set[str]:
    langs = set(CATALOG) | {"en"}
    for d in extra_dirs:
        langs |= {p.stem for p in Path(d).glob("*.json")} if Path(d).is_dir() else set()
    return langs


def detect_language(extra_dirs=(), qt_fallback: str | None = None):
    """Returns (base, locale) of the 1st candidate with translation; otherwise ('en', 'en_US')."""
    avail = available_languages(extra_dirs)
    seen_any = False
    for var in ("MTKLOGO_GUI_LANG", "LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        for part in os.environ.get(var, "").split(":"):
            parsed = _norm(part)
            if not parsed:
                continue
            seen_any = True
            if parsed[0] in avail:
                return parsed
            if parsed[0] == "en":
                return parsed
    if not seen_any and qt_fallback:
        parsed = _norm(qt_fallback)
        if parsed and parsed[0] in avail:
            return parsed
    return "en", "en_US"


def set_language(base: str, locale: str | None = None, extra_dirs=()):
    """Activates the language; loads extra catalogs (JSON) that overwrite the embedded ones."""
    global LANG, LOCALE, _extra
    LANG, LOCALE = base, locale or base
    _extra = {}
    for d in extra_dirs:
        f = Path(d) / f"{base}.json"
        if f.is_file():
            try:
                _extra.update(json.loads(f.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                pass


def _(text: str, **kw) -> str:
    out = _extra.get(text) or CATALOG.get(LANG, {}).get(text) or text
    return out.format(**kw) if kw else out
