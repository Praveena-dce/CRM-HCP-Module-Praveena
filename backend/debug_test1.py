
test1_msg = "Today I met Dr. Prathish at 11:30 AM, it was a Meeting. Attendees were Praveena and Ravi. We discussed Product X efficacy, patient safety, and new treatment guidelines. Materials shared: Product brochure, safety data sheet. Samples distributed: 50 units of Drug Y. Sentiment was positive. Outcomes: Schedule follow-up in 2 weeks, send additional clinical data."
text_lower = test1_msg.lower()

print("'attendees' in text_lower:", 'attendees' in text_lower)
print("'its' in text_lower:", 'its' in text_lower)

# Let's count how many times 'its' appears in test1_msg
import re
matches = list(re.finditer(r'its', test1_msg.lower()))
print("Number of 'its' matches:", len(matches))
for i, m in enumerate(matches):
    print(f"Match {i+1} at position {m.start()}: {test1_msg[m.start():m.start()+10]}...")

# Let's check what 'rfind' returns
idx = text_lower.rfind('its')
print("rfind('its') gives idx:", idx)
if idx != -1:
    print("Substring after idx:", repr(test1_msg[idx + 3:]))
