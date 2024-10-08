BACK_TO_HOME_PAGE_TEXT = "العودة إلى القائمة الرئيسية🔙"

HOME_PAGE_TEXT = "القائمة الرئيسية 🔝"

ACCOUNT_NOT_FOUND_TEXT = (
    "عذراً لم يتم العثور على الحساب"
    " يرجى التأكد من تسجيلك عن طريق الرابط"
    " . او التأكد من كتابتك للـid"
    " بشكل صحيح ، ثم إعاده المحاولة من جديد."
)
ACCOUNT_LEVELS_DATA = (
    "1   100       0.05   1\n"
    "2   200       0.01   2\n"
    "3   500       0.015  3\n"
    "4   1000      0.02   5\n"
    "5   5000      0.025  10\n"
    "6   10000     0.03   20\n"
    "7   25000     0.035  50\n"
    "8   50000     0.04   100\n"
    "9   100000    0.045  200\n"
    "10  250000    0.05   500\n"
    "11  500000    0.055  1000\n"
    "12  1000000   0.06   2000\n"
    "13  2000000   0.065  3000\n"
    "14  5000000   0.07   5000\n"
    "15  75000000  0.075  10000\n"
    "16  10000000  0.08   20000\n"
    "17  12000000  0.085  30000\n"
    "18  15000000  0.09   50000\n"
    "19  20000000  0.095  75000\n"
    "20  25000000  0.10  100000\n"
)

ACCOUNT_LEVELS = {
    i: {
        "lv": i,
        "amount": int(line.split()[1]),
        "perc": float(line.split()[2]),
        "bonus": int(line.split()[3]),
    }
    for i, line in enumerate(ACCOUNT_LEVELS_DATA.splitlines(), start=1)
}


ACCOUNT_LEVELS_TEXT = """LV1    100$.   0.5%.  1
LV2.   200$.  1%.       2
LV3.   500$.   1.5%.   3
LV4.   1k$.      2%.      5
LV5.    5k$.     2.5%.   10
LV6.    10k$.    3%.      20
LV7.   25k$.    3.5%.    50
LV8.   50k$.    4%.       100
LV9.   100k$.  4.5%.  200
LV10.  250k$. 5%.     500
LV11.  500k$.  5.5%.  1k
LV12.  1m$.    6%.     2k
LV13.   2m$.   6.5%.   3k
LV14.   5m$.   7%.       5k
LV15.   7.5m$. 7.5%. 10k
LV16.  10m$.   8%.     20k
LV17.   12m$.   8.5%. 30k
LV18.    15m$.   9%.  50k
LV19.    20m$. 9.5%.  75k
LV20.    25m$. 10%. 100k"""
