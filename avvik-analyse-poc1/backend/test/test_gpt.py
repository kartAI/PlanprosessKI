from backend.services.analysis_service import extract_info_from_text

test_text = """
Energiforbruk
Forslagstiller ønsker solcellepanel. Solcellepaneler tillates ikke i Posebyen på grunn av brannfare.

Arealbruk
Hele planområdet reguleres til “offentlig eller privat tjenesteyting”.
"""

result = extract_info_from_text(test_text)
print(result)