import copy
import json
import os
import re
from typing import Optional

from pywhat.distribution import Distribution


class RegexIdentifier:
    def __init__(self):
        self.distribution = Distribution()

    def check(self, text, distribution: Optional[Distribution] = None):
        if distribution is None:
            distribution = self.distribution
        matches = []

        for string in text:
            for reg in distribution.get_regexes():
                if matched_regex := re.search(reg["Regex"], string, re.UNICODE):
                    reg = copy.copy(reg)  # necessary, when checking phone
                    # numbers from file that may contain
                    # non-international numbers
                    matched = self.clean_text(matched_regex[0])

                    if "Phone Number" in reg["Name"]:
                        number = re.sub(r"[-() ]", "", matched)
                        codes_path = "Data/phone_codes.json"
                        codes_fullpath = os.path.join(
                            os.path.dirname(os.path.abspath(__file__)), codes_path
                        )
                        with open(codes_fullpath, "r", encoding="utf-8") as myfile:
                            codes = json.load(myfile)

                        if locations := [
                            code["name"]
                            for code in codes
                            if number.startswith(code["dial_code"])
                        ]:
                            reg["Description"] = (
                                "Location(s)" + ": " + ", ".join(locations)
                            )

                    matches.append(
                        {
                            "Matched": matched,
                            "Regex Pattern": reg,
                        }
                    )

        return matches

    def clean_text(self, text):
        return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
