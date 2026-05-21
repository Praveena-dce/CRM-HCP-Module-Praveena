
test1_msg = "Today I met Dr. Prathish at 11:30 AM, it was a Meeting. Attendees were Praveena and Ravi. We discussed Product X efficacy, patient safety, and new treatment guidelines. Materials shared: Product brochure, safety data sheet. Samples distributed: 50 units of Drug Y. Sentiment was positive. Outcomes: Schedule follow-up in 2 weeks, send additional clinical data."

print("Test1 message with character indices:")
for i, c in enumerate(test1_msg):
    if i >= 240 and i <= 260:
        print(f"Index {i}: '{c}'")

print("\nSubstring from 240 to 260:", repr(test1_msg[240:260]))
