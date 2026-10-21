import re

CHIP_TERMS = re.compile(
    r"\b(semiconductor|chipmaker|chip design|chip manufacturing|"
    r"foundry|wafer|chiplet|HBM|DRAM|NAND|GPU|ASIC|EDA|"
    r"lithography|EUV|TSMC|ASML|Synopsys|Cadence Design|"
    r"Micron|SK Hynix|GlobalFoundries|Intel Foundry|"
    r"AI accelerator|AI chip|advanced packaging|"
    r"silicon carbide|gallium nitride|semiconductor equipment)\b",
    re.I,
)

AI_INFRA_TERMS = re.compile(
    r"\b(AI infrastructure|AI data cent(er|re)|GPU cluster|"
    r"accelerator demand|AI server|HBM demand|chip supply|"
    r"semiconductor supply chain|semiconductor capex|"
    r"foundry capacity|wafer capacity)\b",
    re.I,
)

def assess_relevance(title, summary=""):
    text = f"{title} {summary}"
    chip_matches = CHIP_TERMS.findall(text)
    infra_matches = AI_INFRA_TERMS.findall(text)

    score = min(5, len(chip_matches) + 2 * bool(infra_matches))
    return {
        "eligible": score > 0,
        "relevance_score": score,
    }
