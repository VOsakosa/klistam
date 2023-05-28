import gettext
import pathlib

translations = gettext.translation("klistam", pathlib.Path(__file__).parents[1] / "locale", fallback=True)
translations.install()
_ = translations.gettext
