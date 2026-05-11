from extract_info import read_pdf  

# Test om pdf gjøres om til tekst
test_path = "uploads/KDPB1264.pdf"
text = read_pdf(test_path)
print(text[:1000])