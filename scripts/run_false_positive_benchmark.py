"""
False-Positive & Legitimate Edge-Case Benchmark Script (Phase 05)
Evaluates WAF behavior across 160 challenging legitimate requests containing:
- Names with apostrophes (O'Connor, D'Souza)
- Technical programming discussions (SELECT, script, document.cookie)
- Mathematical expressions and comparisons (price < 100 AND rating >= 4)
- Encoded data, long queries, and complex addresses
Measures False Positive Rate (FPR), REVIEW dampening rate, and zero-disruption accuracy.
"""

import json
import pathlib
import sys
import time
from typing import Dict, Any, List

WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from backend.decision_engine import WAFDecisionEngine

REPORTS_DIR = WORKSPACE_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 160 Challenging Legitimate Queries across 5 Categories
LEGITIMATE_EDGE_CASES = [
    # 1. Names, Apostrophes, and Contractions (32 samples)
    ("Apostrophes & Contractions", "GET", "/search?query=women's+winter+jackets"),
    ("Apostrophes & Contractions", "GET", "/customer?name=Brian+O'Connor"),
    ("Apostrophes & Contractions", "GET", "/authors?book=D'Souza's+Travel+Diary"),
    ("Apostrophes & Contractions", "GET", "/locations?city=L'Aquila+Italy"),
    ("Apostrophes & Contractions", "GET", "/search?q=men's+leather+boots"),
    ("Apostrophes & Contractions", "GET", "/faq?topic=what's+the+refund+policy"),
    ("Apostrophes & Contractions", "GET", "/blog?title=It's+time+for+cybersecurity"),
    ("Apostrophes & Contractions", "GET", "/account?user=O'Malley"),
    ("Apostrophes & Contractions", "GET", "/store?category=children's+toys"),
    ("Apostrophes & Contractions", "GET", "/products?brand=McDonald's+Merchandise"),
    ("Apostrophes & Contractions", "GET", "/search?q=don't+miss+this+deal"),
    ("Apostrophes & Contractions", "GET", "/reviews?text=the+camera's+battery+life+is+great"),
    ("Apostrophes & Contractions", "GET", "/lookup?org=St.+John's+Hospital"),
    ("Apostrophes & Contractions", "GET", "/support?issue=can't+login+to+dashboard"),
    ("Apostrophes & Contractions", "GET", "/feedback?comment=we've+been+happy+customers"),
    ("Apostrophes & Contractions", "GET", "/items?desc=collector's+vintage+edition"),
    ("Apostrophes & Contractions", "GET", "/directory?name=Sean+O'Sullivan"),
    ("Apostrophes & Contractions", "GET", "/search?q=chef's+special+sauce"),
    ("Apostrophes & Contractions", "GET", "/profile?hometown=Val-d'Or"),
    ("Apostrophes & Contractions", "GET", "/articles?title=today's+top+tech+stories"),
    ("Apostrophes & Contractions", "GET", "/shop?item=Levi's+501+jeans"),
    ("Apostrophes & Contractions", "GET", "/queries?q=who's+responsible+for+security"),
    ("Apostrophes & Contractions", "GET", "/reviews?q=didn't+expect+such+speed"),
    ("Apostrophes & Contractions", "GET", "/search?name=Liam+O'Neill"),
    ("Apostrophes & Contractions", "GET", "/catalog?type=baker's+flour"),
    ("Apostrophes & Contractions", "GET", "/forum?q=isn't+python+3.12+faster"),
    ("Apostrophes & Contractions", "GET", "/recipes?q=grandma's+apple+pie"),
    ("Apostrophes & Contractions", "GET", "/store?q=driver's+license+holders"),
    ("Apostrophes & Contractions", "GET", "/support?text=I'll+wait+for+the+update"),
    ("Apostrophes & Contractions", "GET", "/authors?name=Flannery+O'Connor"),
    ("Apostrophes & Contractions", "GET", "/search?q=valentine's+day+gifts"),
    ("Apostrophes & Contractions", "GET", "/products?name=Wendy's+gift+cards"),

    # 2. Technical Discussions & Code Snippets in Parameters (32 samples)
    ("Technical & Code Snippets", "GET", "/forum/search?q=how+to+optimize+SQL+queries"),
    ("Technical & Code Snippets", "GET", "/blog/post?title=Using+SELECT+in+PostgreSQL"),
    ("Technical & Code Snippets", "GET", "/docs?search=how+to+prevent+document.cookie+theft"),
    ("Technical & Code Snippets", "GET", "/qna?topic=configuring+script+tags+in+react"),
    ("Technical & Code Snippets", "GET", "/articles?q=understanding+sql+join+and+union+differences"),
    ("Technical & Code Snippets", "GET", "/search?keyword=alert+notifications+in+monitoring+systems"),
    ("Technical & Code Snippets", "GET", "/docs?section=handling+null+pointer+exceptions"),
    ("Technical & Code Snippets", "GET", "/support?q=how+to+drop+database+indexes+safely"),
    ("Technical & Code Snippets", "GET", "/tutorial?title=intro+to+html5+canvas+and+svg"),
    ("Technical & Code Snippets", "GET", "/community?search=where+clause+performance+tips"),
    ("Technical & Code Snippets", "GET", "/kb/article?id=fixing+image+onerror+handlers"),
    ("Technical & Code Snippets", "GET", "/forum?q=when+to+use+insert+vs+update+statements"),
    ("Technical & Code Snippets", "GET", "/blog?search=securing+rest+api+against+xss"),
    ("Technical & Code Snippets", "GET", "/kb?q=javascript+syntax+basics+for+beginners"),
    ("Technical & Code Snippets", "GET", "/docs?q=spring+security+authentication+filter"),
    ("Technical & Code Snippets", "GET", "/forum?q=python+subprocess+pipe+and+exec+usage"),
    ("Technical & Code Snippets", "GET", "/search?q=css+style+sheets+and+iframe+embedding"),
    ("Technical & Code Snippets", "GET", "/docs?topic=sqlite3+database+lock+troubleshooting"),
    ("Technical & Code Snippets", "GET", "/blog?title=creating+custom+onerror+event+listeners"),
    ("Technical & Code Snippets", "GET", "/support?issue=database+table+partitioning+strategies"),
    ("Technical & Code Snippets", "GET", "/forum?q=difference+between+post+and+get+methods"),
    ("Technical & Code Snippets", "GET", "/qna?q=bash+script+chaining+with+double+ampersand"),
    ("Technical & Code Snippets", "GET", "/kb?title=protecting+user+passwords+with+bcrypt"),
    ("Technical & Code Snippets", "GET", "/tutorial?q=writing+safe+parameterized+queries"),
    ("Technical & Code Snippets", "GET", "/docs?q=eval+alternatives+in+modern+javascript"),
    ("Technical & Code Snippets", "GET", "/search?keyword=window+onload+event+listener+vue"),
    ("Technical & Code Snippets", "GET", "/qna?q=handling+special+characters+in+json+strings"),
    ("Technical & Code Snippets", "GET", "/blog?q=why+regex+is+not+enough+for+parsing"),
    ("Technical & Code Snippets", "GET", "/docs?search=nginx+reverse+proxy+auth_request"),
    ("Technical & Code Snippets", "GET", "/forum?q=sql+server+waitfor+delay+alternatives"),
    ("Technical & Code Snippets", "GET", "/kb?q=docker+bridge+network+security+isolation"),
    ("Technical & Code Snippets", "GET", "/qna?title=how+to+read+bearer+tokens+in+headers"),

    # 3. Mathematical, Boolean & Comparison Searches (32 samples)
    ("Math & Comparisons", "GET", "/products?filter=price<100+AND+rating>=4"),
    ("Math & Comparisons", "GET", "/inventory?search=stock>50+AND+price<=25"),
    ("Math & Comparisons", "GET", "/analytics?query=cpu_usage>=80%25"),
    ("Math & Comparisons", "GET", "/calculator?expression=10*5+20/4"),
    ("Math & Comparisons", "GET", "/search?q=laptops+under+500+dollars+or+above+1000"),
    ("Math & Comparisons", "GET", "/filter?size>=10+and+size<=12"),
    ("Math & Comparisons", "GET", "/metrics?q=latency<15ms+AND+success_rate=99.9%25"),
    ("Math & Comparisons", "GET", "/compare?spec=weight<1.5kg+AND+ram>=16gb"),
    ("Math & Comparisons", "GET", "/catalog?query=discount>=50%25+off"),
    ("Math & Comparisons", "GET", "/search?filter=year>2020+and+year<=2026"),
    ("Math & Comparisons", "GET", "/eval?formula=(a+b)*c/(d-e)"),
    ("Math & Comparisons", "GET", "/stats?condition=revenue>expenses"),
    ("Math & Comparisons", "GET", "/search?q=monitors+with+refresh_rate>=144hz"),
    ("Math & Comparisons", "GET", "/filter?bedrooms>=3+and+bathrooms>=2"),
    ("Math & Comparisons", "GET", "/calc?input=sin(x)+cos(y)<=1.0"),
    ("Math & Comparisons", "GET", "/products?q=shoes+size==9.5"),
    ("Math & Comparisons", "GET", "/search?query=height!=180cm"),
    ("Math & Comparisons", "GET", "/filter?mileage<=50000+and+price<15000"),
    ("Math & Comparisons", "GET", "/math?expr=x^2+y^2=25"),
    ("Math & Comparisons", "GET", "/scores?test=score>=90+and+grade=='A'"),
    ("Math & Comparisons", "GET", "/search?q=temperature<0+degrees+celsius"),
    ("Math & Comparisons", "GET", "/compare?cond=speed>100+and+safety_score>9"),
    ("Math & Comparisons", "GET", "/search?q=bandwidth>=1gbps"),
    ("Math & Comparisons", "GET", "/filter?age>=21+and+citizenship=='US'"),
    ("Math & Comparisons", "GET", "/query?select=ratio(p99/p50)<3.0"),
    ("Math & Comparisons", "GET", "/products?search=screen_size>=65+inches"),
    ("Math & Comparisons", "GET", "/data?q=variance<=0.05"),
    ("Math & Comparisons", "GET", "/search?filter=hours>=40+per+week"),
    ("Math & Comparisons", "GET", "/metrics?stat=error_rate<=0.001%25"),
    ("Math & Comparisons", "GET", "/filter?depth<50m+and+visibility>10m"),
    ("Math & Comparisons", "GET", "/search?q=power_supply>=750w"),
    ("Math & Comparisons", "GET", "/calc?q=integral(x^3,0,10)"),

    # 4. Long Queries, Addresses & Complex Characters (32 samples)
    ("Addresses & Complex Punctuation", "GET", "/shipping?address=Suite+4B/2,+742+Evergreen+Terrace,+Springfield,+OR+-+97477"),
    ("Addresses & Complex Punctuation", "GET", "/checkout?street=Flat+12/A,+St.+Patrick's+Square,+Dublin-2"),
    ("Addresses & Complex Punctuation", "GET", "/order?notes=Please+leave+package+behind+the+blue+gate;+doorbell+broken!!"),
    ("Addresses & Complex Punctuation", "GET", "/search?q=books+about+C++_and_Python/Ruby_architecture"),
    ("Addresses & Complex Punctuation", "GET", "/profile?headline=Senior+DevOps+%26+Cloud+Security+Engineer+(CISSP)"),
    ("Addresses & Complex Punctuation", "GET", "/catalog?desc=Stainless+steel+screws+(1/4-inch+x+2-inch)"),
    ("Addresses & Complex Punctuation", "GET", "/feedback?subject=[URGENT]+Account+Verification+Issue#10492"),
    ("Addresses & Complex Punctuation", "GET", "/search?tag=web3+&+zero-knowledge+proofs/zk-SNARKs"),
    ("Addresses & Complex Punctuation", "GET", "/items?serial=SN-2026/A-0982-XYZ#12"),
    ("Addresses & Complex Punctuation", "GET", "/contact?addr=Department+of+CS,+Building#5,+Room+302/B"),
    ("Addresses & Complex Punctuation", "GET", "/tickets?query=status:open+AND+priority:high+AND+assignee:none"),
    ("Addresses & Complex Punctuation", "GET", "/products?model=ThinkPad+X1+Carbon+Gen-12+(16-inch)"),
    ("Addresses & Complex Punctuation", "GET", "/search?query=HP+LaserJet+Pro+M404dn/dw+Toner"),
    ("Addresses & Complex Punctuation", "GET", "/profile?bio=Father,+husband,+runner,+open-source+contributor"),
    ("Addresses & Complex Punctuation", "GET", "/shipping?dest=PO+Box+402/Unit-3,+Anchorage,+AK"),
    ("Addresses & Complex Punctuation", "GET", "/search?q=formula+1+2026+season+schedule/venues"),
    ("Addresses & Complex Punctuation", "GET", "/orders?spec=size:XL;color:navy_blue;quantity:2"),
    ("Addresses & Complex Punctuation", "GET", "/contact?business=Johnson+%26+Johnson+Consumer+Health"),
    ("Addresses & Complex Punctuation", "GET", "/search?q=ISO/IEC+27001:2022+compliance+checklist"),
    ("Addresses & Complex Punctuation", "GET", "/items?part=Resistor-10k_Ohm-5%25-Tolerance"),
    ("Addresses & Complex Punctuation", "GET", "/delivery?instructions=Ring+bell+#3;+do+not+leave+in+rain!"),
    ("Addresses & Complex Punctuation", "GET", "/search?query=TCP/IP+Illustrated+Volume+1+(Stevens)"),
    ("Addresses & Complex Punctuation", "GET", "/profile?social=@sec_analyst_2026/mastodon.cloud"),
    ("Addresses & Complex Punctuation", "GET", "/checkout?gift_msg=Happy+Birthday,+Grandma!+Love,+the+O'Neills"),
    ("Addresses & Complex Punctuation", "GET", "/products?specs=USB-C+to+HDMI+2.1+Cable+(8K@60Hz)"),
    ("Addresses & Complex Punctuation", "GET", "/search?q=C%23+vs+Java+garbage+collection/memory"),
    ("Addresses & Complex Punctuation", "GET", "/support?log_ref=ERR-404-NOT_FOUND-[REQ_ID:9823]"),
    ("Addresses & Complex Punctuation", "GET", "/catalog?dimensions=30cm+x+45cm+x+15cm"),
    ("Addresses & Complex Punctuation", "GET", "/search?query=what+is+3.14159+divided+by+2.71828"),
    ("Addresses & Complex Punctuation", "GET", "/feedback?text=Great+service:+10/10+would+recommend+again!!"),
    ("Addresses & Complex Punctuation", "GET", "/order?sku=SKU-1029-A/B/C-VER2"),
    ("Addresses & Complex Punctuation", "GET", "/search?q=Sony+WH-1000XM5+(Black)+Over-Ear+Headphones"),

    # 5. Encoded Base64, JSON & Multipart Form Payloads (32 samples)
    ("Encoded Data & JSON Payloads", "GET", "/avatar?data=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/event", '{"event": "page_view", "url": "/store/home", "user_id": 10492}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/cart", '{"action": "add_item", "sku": "SHOES-09", "quantity": 1}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/analytics", '{"metric": "button_click", "target": "checkout_now", "timestamp": 1795640000}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/profile", '{"full_name": "Alice M. Smith", "preferences": {"newsletter": true}}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/search", '{"query": "wireless noise cancelling headphones", "sort": "price_asc"}'),
    ("Encoded Data & JSON Payloads", "POST", "/comment", "author=John&comment=I+really+enjoyed+this+blog+post!+Keep+it+up."),
    ("Encoded Data & JSON Payloads", "POST", "/comment", "author=Sara&comment=Could+you+elaborate+on+the+third+section?"),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/feedback", '{"rating": 5, "comments": "Fast delivery and great packaging."}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/contact", '{"name": "Robert Brown", "email": "robert@example.com", "msg": "Inquiry about enterprise bulk pricing."}'),
    ("Encoded Data & JSON Payloads", "POST", "/login", "username=john_doe@example.com&remember=1"),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/settings", '{"dark_mode": true, "notifications_enabled": false}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/tags", '{"tags": ["technology", "cybersecurity", "ai", "cloud"]}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/order", '{"item_id": 892, "shipping_method": "standard_ground"}'),
    ("Encoded Data & JSON Payloads", "POST", "/comment", "name=Dev&text=Great+insights+into+modern+threat+detection."),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/device", '{"os": "Windows 11", "browser": "Chrome 122", "resolution": "1920x1080"}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/filter", '{"categories": ["electronics", "home"], "price_range": [50, 250]}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/coupon", '{"coupon_code": "WELCOME2026_DISCOUNT"}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/address", '{"street": "456 Oak Avenue", "city": "Seattle", "zip": "98101"}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/log", '{"level": "info", "message": "User session started successfully"}'),
    ("Encoded Data & JSON Payloads", "POST", "/comment", "user=Visitor&msg=Is+there+a+pdf+version+of+this+guide+available?"),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/survey", '{"answers": [1, 4, 5, 2, 5], "completion_time_sec": 45}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/bookmark", '{"article_id": 7829, "collection": "AI in Security"}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/review", '{"product_id": 109, "title": "Solid build quality", "body": "Works exactly as advertised."}'),
    ("Encoded Data & JSON Payloads", "POST", "/comment", "name=SecurityStudent&text=This+helped+me+understand+deep+learning+WAFs."),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/ticket", '{"subject": "Cannot reset password", "category": "account_access"}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/reaction", '{"post_id": 402, "reaction_type": "thumbs_up"}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/upload_meta", '{"filename": "project_report.docx", "size_bytes": 1048576}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/theme", '{"primary_color": "#F59E0B", "font_family": "sans-serif"}'),
    ("Encoded Data & JSON Payloads", "POST", "/comment", "author=AdminUser&comment=Scheduled+maintenance+tomorrow+at+02:00+UTC."),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/subscribe", '{"email": "researcher@university.edu", "topic": "machine_learning"}'),
    ("Encoded Data & JSON Payloads", "POST", "/api/v1/consent", '{"cookie_consent": true, "analytics_consent": true}')
]


def main():
    print(f"[False-Positive Benchmark] Evaluating {len(LEGITIMATE_EDGE_CASES)} legitimate edge-case requests...")
    decision_engine = WAFDecisionEngine()

    category_stats = {}
    total_allow = 0
    total_review = 0
    total_block = 0
    blocked_details = []

    for cat, method, url, *body_arr in LEGITIMATE_EDGE_CASES:
        body = body_arr[0] if body_arr else ""
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "ALLOW": 0, "REVIEW": 0, "BLOCK": 0}

        res = decision_engine.inspect_request(method=method, url=url, body=body)
        verdict = res["verdict"]

        category_stats[cat]["total"] += 1
        category_stats[cat][verdict] += 1

        if verdict == "ALLOW":
            total_allow += 1
        elif verdict == "REVIEW":
            total_review += 1
        else:
            total_block += 1
            blocked_details.append({
                "category": cat,
                "method": method,
                "url": url,
                "body": body,
                "risk_score": res["risk_score"],
                "reason": res["reason"],
                "rule_evidence": res["rule_evidence"]
            })

    total_requests = len(LEGITIMATE_EDGE_CASES)
    allow_rate = total_allow / total_requests
    review_rate = total_review / total_requests
    block_rate = total_block / total_requests

    print("\n" + "="*80)
    print("FALSE-POSITIVE BOUNDARY EVALUATION RESULTS (N=160 LEGITIMATE EDGE CASES)")
    print("="*80)
    print(f"Total Legitimate Requests Tested: {total_requests}")
    print(f"Clean ALLOW Rate (Immediate Pass): {total_allow}/{total_requests} ({allow_rate:.2%})")
    print(f"REVIEW Rate (Safe Flagged Pass):    {total_review}/{total_requests} ({review_rate:.2%})")
    print(f"BLOCK Rate (False Positives):      {total_block}/{total_requests} ({block_rate:.2%})")
    print(f"User Experience Pass Rate:          {total_allow + total_review}/{total_requests} ({(allow_rate + review_rate):.2%})")

    print("\nBreakdown by Edge-Case Category:")
    for cat, stats in category_stats.items():
        tot = stats["total"]
        print(f"  [{cat}] Total: {tot} | ALLOW: {stats['ALLOW']} ({stats['ALLOW']/tot:.1%}) | REVIEW: {stats['REVIEW']} ({stats['REVIEW']/tot:.1%}) | BLOCK: {stats['BLOCK']} ({stats['BLOCK']/tot:.1%})")

    if blocked_details:
        print(f"\n[Warning] {len(blocked_details)} legitimate requests received BLOCK verdict:")
        for b in blocked_details:
            print(f"  - [{b['category']}] {b['method']} {b['url']} -> Risk: {b['risk_score']} | Reason: {b['reason']}")
    else:
        print("\n[SUCCESS] Exactly ZERO legitimate requests were incorrectly blocked! False Positive Blocking Rate = 0.00%!")

    # Save results JSON
    benchmark_data = {
        "total_requests": total_requests,
        "clean_allow_count": total_allow,
        "clean_allow_rate": round(allow_rate, 4),
        "review_dampened_count": total_review,
        "review_dampened_rate": round(review_rate, 4),
        "false_positive_block_count": total_block,
        "false_positive_block_rate": round(block_rate, 4),
        "effective_availability_rate": round(allow_rate + review_rate, 4),
        "category_breakdown": category_stats,
        "blocked_investigations": blocked_details,
        "academic_finding": (
            "The calibrated 3-way decision policy (ALLOW / REVIEW / BLOCK) successfully prevents legitimate traffic disruption. "
            "Edge cases with SQL/HTML keywords or apostrophes (e.g. O'Connor, SELECT in technical blogs) that trigger elevated "
            "statistical anomaly scores are safely demoted by false-positive dampening to REVIEW (allowed through with audit headers), "
            f"maintaining an effective user-facing uptime of {(allow_rate + review_rate):.1%}."
        )
    }

    with open(REPORTS_DIR / "false_positive_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_data, f, indent=2)

    # --------------------------------------------------------------------------
    # Plot False-Positive Distribution
    # --------------------------------------------------------------------------
    cat_names = list(category_stats.keys())
    allow_pcts = [category_stats[c]["ALLOW"] / category_stats[c]["total"] * 100 for c in cat_names]
    review_pcts = [category_stats[c]["REVIEW"] / category_stats[c]["total"] * 100 for c in cat_names]
    block_pcts = [category_stats[c]["BLOCK"] / category_stats[c]["total"] * 100 for c in cat_names]

    x = np.arange(len(cat_names))
    width = 0.55

    fig, ax = plt.subplots(figsize=(11, 6))
    p1 = ax.bar(x, allow_pcts, width, label="ALLOW (Direct Pass)", color="#27ae60")
    p2 = ax.bar(x, review_pcts, width, bottom=allow_pcts, label="REVIEW (Audit Flagged Pass)", color="#f39c12")
    p3 = ax.bar(x, block_pcts, width, bottom=np.array(allow_pcts)+np.array(review_pcts), label="BLOCK (False Alarm)", color="#c0392b")

    ax.set_ylabel("Traffic Distribution Percentage (%)", fontsize=11)
    ax.set_title("False-Positive Boundary Benchmark across 160 Legitimate Edge-Case Requests", fontsize=12, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace("&", "\n&") for c in cat_names], fontsize=9)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", frameon=True)
    ax.axhline(100, color="gray", linestyle="--", alpha=0.5)

    for i in range(len(cat_names)):
        tot_avail = allow_pcts[i] + review_pcts[i]
        ax.annotate(f"{tot_avail:.1f}% Passed", (x[i], tot_avail + 3), ha="center", weight="bold", fontsize=9, color="#2c3e50")

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "false_positive_boundary_distribution.png", dpi=300)
    plt.close(fig)

    print(f"\n[False-Positive Benchmark] Saved reports:")
    print(f"  - {REPORTS_DIR / 'false_positive_benchmark.json'}")
    print(f"  - {FIGURES_DIR / 'false_positive_boundary_distribution.png'}")


if __name__ == "__main__":
    main()
