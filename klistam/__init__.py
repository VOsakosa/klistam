import gettext
import pathlib

translations = gettext.translation("klistam", pathlib.Path(__file__).parents[1] / "locale")
translations.install()
_ = translations.gettext
