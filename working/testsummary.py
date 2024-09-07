
import mdbutilities.mdbutilities as MU
import textwords as SUM


file_get = r"C:\git\ms\azure-docs-pr\articles\azure-cache-for-redis\cache-dotnet-core-quickstart.md"
rawtext = MU.get_textfromfile(file_get)
summary = SUM.get_top_ten(rawtext)
print(summary)