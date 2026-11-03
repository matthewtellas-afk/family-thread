# Builds collateral/people.json, relationships.json, notes.json from the book data already embedded in app.js.
# Usage (from the repo root): python3 collateral/build.py
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'collateral')
d = {}
for line in open(os.path.join(ROOT, 'app.js'), encoding='utf-8'):
    m = re.match(r'const (DATA|EXTRA|EVENTS|CLAIMS|STORIES|CLIPPINGS|CENSUS) = (.*);\s*$', line)
    if m: d[m.group(1)] = json.loads(m.group(2))
E = d['EVENTS']; TREE = {p['id']: p for p in d['DATA'] + d['EXTRA']}
CL = {c['id']: c for c in d['CLAIMS']['claims']}
TYPE = {'b': 'born', 'd': 'died', 'm': 'married'}
def ev(i):
    e = E[i]; return f"{TYPE[e['type']]} {e['year']}-{e['month']:02d}-{e['day']:02d} (“{e['who']}”)"
def cal(*ix): return {'t': 'Family book calendar (Hillman 1991), as embedded in app.js EVENTS: ' + '; '.join(ev(i) for i in ix)}
def claim(cid): c = CL[cid]; return {'t': f"Family book p.{c['page']}, claim '{cid}' in app.js CLAIMS: “{c['claim']}”"}
def story(pid, txt): return {'t': f"app.js STORIES[{pid}] (retold from records/obituary): “{txt}”"}
def clip(pid, txt): return {'t': f"app.js CLIPPINGS[{pid}] (retold, not a real article): “{txt}”"}
def yr(i): return str(E[i]['year'])

people, notes, rels = [], [], []
SRC = {'janice-fratzke': '1950 census; obituary (as retold in repo)', 'george-anglin': 'obituary (as retold in repo)', 'johnny-chillas': 'family book (Hillman 1991); obituary-based story'}
def person(id, name, line, born='', died='', ev_ix=(), sex='', father=None, mother=None, src=(), conf='uncertain', verdict='book', note='', living=False, topic='Collateral', conflict=''):
    assert id not in TREE, id
    p = {'id': id, 'gen': None, 'name': name, 'born': born, 'place': '', 'died': '(living)' if living == 'yes' else died,
         'line': line, 'source': SRC.get(id) or ('family book (Hillman 1991), calendar' if ev_ix else 'family book (Hillman 1991)'), 'father': father, 'mother': mother}
    if sex: p['sex'] = sex
    people.append(p)
    srcs = ([cal(*ev_ix)] if ev_ix else []) + list(src)
    n = {'id': 'add-' + id, 'people': [id], 'topic': topic, 'page': None, 'claim': f"Add {name} to the tree" + (f" (b. {born})" if born else '') + (f" (d. {died})" if died and died != '(living)' else '') + '.',
         'verdict': verdict, 'confidence': conf, 'note': note, 'sources': srcs}
    if conflict: n['conflict'] = conflict
    if living: n['possiblyLiving'] = True
    notes.append(n)
def rel(kind, a, b, conf, note, src, date='', stated=True, verdict='book', conflict=''):
    r = {'id': f"rel-{kind}-{a}-{b}", 'type': kind, 'a': a, 'b': b, 'date': date, 'confidence': conf, 'statedInSource': stated, 'verdict': verdict, 'note': note, 'sources': src}
    if conflict: r['conflict'] = conflict
    rels.append(r)

DAYNOTE = 'Only the year is used: where the calendar overlaps people already verified in this tree, its day is often off by one or two.'
POSS = 'No death date in the sources and born recently enough to be living, so treat as possibly living: name and year only, nothing else.'

# ---------------- Tellas: children of John Thomas Tellas I & Margaret Godert ----------------
person('jerry', 'Jeremiah "Jerry" Tellas', 'Tellas', yr(5), yr(227), (5, 227), 'M', 'john1', 'margodert',
       [claim('racer'), claim('kansas'), clip('charles', 'Jerry Tellas has returned home from Kansas, where he and his brother Charles spent several seasons')],
       'likely', 'book', 'The book calls Ray Tellas the son of “John’s son Jerry,” and the Kansas story makes Jerry and Charlie brothers. Margaret Godert as mother is inferred from the 1864 marriage and his 1866 birth; no passage names her.')
person('rosa-spangler', 'Rosa E. Spangler Tellas', 'Spangler', yr(141), '', (141, 217), 'F', src=[], conf='likely', note='The calendar lists a Rosa E. (Spangler) Tellas born 1868 and a marriage of “Jeremiah & Rosa Tellas” in 1889. They are taken to be the same Rosa. No death date. ' + DAYNOTE)
person('ray-tellas', 'Raymond J. "Ray" Tellas', 'Tellas', yr(21), yr(155), (21, 155, 198), 'M', 'jerry', None, [claim('racer')], 'confirmed', 'conflict',
       'Ray, the dirt-track racer, son of Jerry. The racing-history source cited in the book claim confirms the August 1940 crash at Franklin. His mother is not named.',
       conflict='The calendar puts his death on 3 August 1940. The book claim and the racing source say 11 August 1940. The calendar’s many “3 August” entries look like an extraction artifact.')
person('elizabeth-ray', 'Elizabeth Tellas (wife of Raymond J.)', 'Tellas', '', '', (198,), 'F', conf='uncertain', note='Known only from the calendar’s 1930 marriage of “Raymond J & Elizabeth Tellas.” No maiden name or dates. She could be the Elizabeth V. Tellas born 1909, but nothing ties them together.')
person('john2', 'John Thomas Tellas II', 'Tellas', yr(73), yr(112), (73, 112), 'M', 'john1', 'margodert', [claim('birth-1836'), claim('farm')], 'likely', 'book',
       'The book claims call him John I’s son: he wrote the family Bible note and trained race horses at the Indiana State Fairgrounds. Margaret as mother is inferred from the dates, not stated.')
person('sophia-link', 'Sophia Link Tellas', 'Link', '', yr(200), (200, 3, 205), 'F', conf='likely', note='Wife of John Thomas Tellas II. The calendar names “John & Sophia Tellas II” as parents of two infants and lists Sophia (Link) Tellas’s death in 1925.')
person('inf-john2-1898', 'Infant of John & Sophia Tellas II (1898)', 'Tellas', yr(205), yr(205), (205,), '', 'john2', 'sophia-link', conf='likely', note='The calendar entry reads “& d. inf of John & Sophia Tellas II,” i.e. born and died 1898. The parents are named in the entry itself.')
person('inf-john2-1903', 'Infant of John & Sophia Tellas II (1903)', 'Tellas', yr(3), yr(8), (3, 8), '', 'john2', 'sophia-link', conf='likely', note='Born and died January 1903, per the calendar. The parents are named in the entry.')
person('dora-tellas', 'Dora E. Tellas Christie', 'Tellas', yr(116), yr(201), (116, 201), 'F', conf='uncertain',
       note='Born a Tellas in 1872, so probably a daughter of John I and Margaret, but no passage in this repo says so. Left unlinked. Her husband’s first name is not given.')
person('annie-tellas', 'Anna "Annie" Tellas Falderman Bailey', 'Tellas', yr(83), yr(177), (83, 177, 132), 'F', 'john1', 'margodert', [claim('annie')], 'likely', 'book',
       'The book calls her “John’s daughter Annie (Tellas) Falderman.” She was head nurse of an Indianapolis orphanage and nursed soldiers at Fort Benjamin Harrison. Her 1940 obituary is from Twentynine Palms, California. The calendar records her death as “Anna (Tellas) Bailey/Falderman.” Margaret as mother is inferred from the dates.')
person('alice-tellas', 'Alice Tellas Swango', 'Tellas', yr(90), yr(33), (90, 33, 207), 'F', conf='uncertain',
       note='Born a Tellas in 1878 and married Henry E. Swango in 1892. Probably a daughter of John I and Margaret, but no passage in this repo says so. Left unlinked.',
       conflict='A marriage in November 1892 would make her 14, if the 1878 birth year is right. One of the two calendar years may be wrong.')
person('margaret-may-tellas', 'Margaret May Tellas', 'Tellas', yr(145), yr(111), (145, 111), 'F', conf='uncertain',
       note='The calendar has “Margaret M Tellas” born 1880 and “Margaret May Tellas” died 1881. They are taken to be one infant. She may be the child of John I and Margaret who “died as a baby” (STORIES[margodert]), but that is not stated.')
person('william-t-tellas', 'William T. Tellas', 'Tellas', yr(29), yr(44), (29, 44, 71), 'M', conf='uncertain', note='Born 1883, died 1942, married Anna Pieper in 1902. Probably a son of John I and Margaret, but not stated. Left unlinked.')
person('anna-pieper', 'Anna L. Pieper Tellas', 'Pieper', '', yr(139), (139, 71), 'F', conf='likely', note='The calendar lists the 1902 marriage of “William & Anna (Pieper) Tellas” and her death in 1934.')
person('ida-f-tellas', 'Ida F. Tellas', 'Tellas', yr(23), '', (23,), 'F', conf='uncertain', note='Only a birth entry (1884). This calendar often lists women under married names, so she could be a daughter born a Tellas or a wife. Unplaced.',
       conflict='If she were a ninth child of John I and Margaret, that would contradict “raised eight children” in STORIES[margodert].')
person('benjamin-tellas', 'Benjamin F. Tellas', 'Tellas', yr(110), yr(43), (110, 43), 'M', conf='uncertain', note='Two entries: “Benjamin F Tellas” born 1893 and “Benjamin Tellas” died 1906. They are merged here as one boy who died at about 12. That merge is uncertain. Unplaced.')

# ---------------- Tellas: children of Charles Lewis Tellas & Sarah Chillas ----------------
person('john-louis-tellas', 'John Louis Tellas', 'Tellas', yr(46), yr(81), (46, 81, 92, 181), 'M', 'charles', 'sarah', [claim('charlie-sarah')], 'likely', 'book',
       'The book names “John L.” as one of Charlie and Sarah’s three World War I sons. Married Anna in 1920 and Mabel in 1930, per the calendar.')
person('anna-herbert', 'Anna F. Herbert Tellas', 'Herbert', '', yr(68), (68, 92), 'F', conf='uncertain', note='Died 1928. Possibly the Anna who married John Louis Tellas in 1920, but the calendar gives that bride no maiden name.')
person('mabel-black', 'Mabel Black Tellas', 'Black', yr(56), yr(196), (56, 196, 181), 'F', conf='uncertain', note='“Mabel Tellas” born 1904 and “Mabel (Black) Tellas” died 1985 are merged as one person, the Mabel who married John Louis Tellas in 1930. The calendar lists women under their married names, which is what supports the merge. Both the merge and the marriage link are uncertain.')
person('thomas-f-tellas', 'Thomas F. Tellas', 'Tellas', yr(218), '', (218, 121), 'M', 'charles', 'sarah', [claim('charlie-sarah')], 'likely', 'book',
       'One of Charlie and Sarah’s three World War I sons, per the book. The calendar entry “Thomas F & Clara E Tellas” (1921) is marked as a death, but a couple’s name points to a marriage. No death date found.')
person('clara-koebbe', 'Clara E. Koebbe Tellas', 'Koebbe', yr(98), yr(62), (98, 62, 121), 'F', conf='likely', note='Probably the Clara E. of “Thomas F & Clara E Tellas” (1921). Born 1900, died 1983.')
person('frank-garrett-tellas', 'Frank Garrett Tellas', 'Tellas', yr(74), '', (74, 148), 'M', 'charles', 'sarah', [claim('other-matthew')], 'likely', 'book',
       'The book names Frank Garrett Tellas as Charlie and Sarah’s son and the grandfather of the other Matthew Tellas. The calendar lists “Frank G Tellas” born 1903 and “Frank & Elizabeth Tellas” married 1925.')
person('elizabeth-frank', 'Elizabeth Tellas (wife of Frank G.)', 'Tellas', '', '', (148,), 'F', conf='uncertain', note='Known only from the 1925 marriage entry. No maiden name or dates.')
person('anna-tellas-thackery', 'Anna Tellas Thackery', 'Tellas', yr(48), yr(34), (48, 34, 80), 'F', 'charles', 'sarah', [claim('wmck'), story('wmck', 'In 1921 he married Allie Mae Thackery, two months after his sister Anna married Allie’s brother Walter.')],
       'likely', 'consistent', 'William McKinley’s sister Anna, who married Walter Thackery in April 1921. The calendar’s “Anna Thackery” born 1900 (listed under her married name) and “Anna (Tellas) Thackery” died 1982 are merged.')
person('walter-thackery', 'Walter L. Thackery', 'Thackery', yr(220), yr(103), (220, 103, 80), 'M', 'jfrank', 'ida', [claim('wmck')], 'likely', 'consistent',
       'The book claim’s note says Allie and Walter are both children of John Franklin Thackery and Ida Mae Price. That makes the Tellas and Thackery families related twice over.')
person('inf-wmck-1921', 'Infant of William & Allie (Thackery) Tellas (1921)', 'Tellas', yr(107), '', (107,), '', 'wmck', 'allie', conf='uncertain',
       note='The calendar entry reads “n. William & Allie (Thackery) Tellas,” a birth in June 1921. The “n.” is probably a garbled “inf.” The parents are named in the entry.',
       conflict='A June 1921 birth comes two days before the 22 June 1921 wedding given in the book claim ‘wmck’. Allie is said to have raised six children, so this may be a seventh who died young, or a date error.')

# ---------------- William McKinley & Allie's children (obituary + story + calendar) ----------------
for pid, nm, ix, extra in [
    ('shirley-ash', 'Shirley M. Tellas Ash', 72, [clip('wmck', 'Of their six children Shirley was the third… Shirley Tellas Ash farmed, rose from teller to bank branch manager')]),
    ('mildred-boyles', 'Mildred Tellas Boyles', 45, []), ('marjorie-williams', 'Marjorie Tellas Williams', 114, []),
    ('betty-buell', 'Betty Tellas Buell', 42, []), ('william-a-tellas', 'William A. Tellas', 211, [])]:
    first = nm.split()[0]
    person(pid, nm, 'Tellas', yr(ix), '', (ix,), 'M' if first == 'William' else 'F', 'wmck', 'allie',
           [story('allie', 'raised six children: Marjorie, Mildred, Shirley, Betty, William and Douglas'), claim('doug')] + extra,
           'confirmed' if pid == 'shirley-ash' else 'likely', 'consistent',
           f'STORIES[allie] and Doug’s obituary (“youngest of six”) name {first} as a child of William McKinley and Allie. The birth year comes from a calendar entry listed under the married name, so matching the two is the inference. ' + POSS,
           living=True, topic='Doug’s siblings',
           conflict='STORIES[allie] lists Marjorie first, but the calendar puts Mildred (1924) and Shirley (1926) before Marjorie (1927). CLIPPINGS[wmck] calls Shirley the third child, which fits only if the 1921 infant is counted.' if pid in ('marjorie-williams', 'shirley-ash') else '')
for pid, nm, ix, sp in [('vernon-boyles', 'Vernon Boyles', 41, 'Mildred'), ('clare-ash', 'Clare Ash II', 102, 'Shirley'), ('richard-buell', 'C. Richard Buell', 213, 'Betty')]:
    person(pid, nm, nm.split()[-1] if 'II' not in nm else 'Ash', yr(ix), '', (ix,), 'M', conf='uncertain', note=f'Shares the married surname of {sp}. Probably her husband, but the calendar extract does not say so. ' + POSS, living=True)
person('earl-williams', 'C. Earl Williams', 'Williams', yr(204), yr(78), (204, 78), 'M', conf='uncertain', note='Shares the married surname of Marjorie (Tellas) Williams. Probably her husband, but not stated.')

# ---------------- Tellas-surnamed people the calendar does not place ----------------
for pid, nm, b, dd, sex, ln in [
    ('harry-w-tellas', 'Harry W. Tellas', 10, None, 'M', 'Tellas'), ('donald-l-tellas', 'Donald L. Tellas', 11, None, 'M', 'Tellas'),
    ('clyde-tellas', 'Clyde Tellas', None, 22, 'M', 'Tellas'), ('c-arthur-tellas', 'C. Arthur Tellas', 24, 191, 'M', 'Tellas'),
    ('wanda-hicks', 'Wanda Hicks Tellas', 30, None, 'F', 'Hicks'), ('virginia-bernabe', 'Virginia Bernabe Tellas', 35, None, 'F', 'Bernabe'),
    ('martha-h-tellas', 'Martha H. Tellas', 37, None, 'F', 'Tellas'), ('elizabeth-v-tellas', 'Elizabeth V. Tellas', 64, None, 'F', 'Tellas'),
    ('dorothy-m-tellas', 'Dorothy M. Tellas', 113, None, 'F', 'Tellas'), ('marie-tellas', 'Marie Tellas', 99, None, 'F', 'Tellas'),
    ('ida-henderson', 'Ida Henderson Tellas', None, 100, 'F', 'Henderson'), ('grace-tellas', 'Grace Tellas', None, 95, 'F', 'Tellas'),
    ('elmer-j-tellas', 'Elmer J. Tellas', 222, 122, 'M', 'Tellas'), ('catherine-l-tellas', 'Catherine L. Tellas', 154, None, 'F', 'Tellas'),
    ('robert-f-tellas', 'Robert F. Tellas', 167, None, 'M', 'Tellas'), ('robert-g-tellas', 'Robert G. Tellas', None, 140, 'M', 'Tellas'),
    ('myrna-m-tellas', 'Myrna M. Tellas', 190, None, 'F', 'Tellas'), ('edward-f-tellas', 'Edward F. Tellas', None, 173, 'M', 'Tellas'),
    ('florence-tellas', 'Florence Tellas', None, 93, 'F', 'Tellas'), ('zella-ewell', 'Zella Ewell Tellas Jordan', 164, None, 'F', 'Ewell'),
    ('naomi-tellas-jones', 'Naomi Tellas Jones', 129, None, 'F', 'Tellas')]:
    ix = tuple(i for i in (b, dd) if i is not None)
    by = yr(b) if b is not None else ''
    living = dd is None and b is not None and E[b]['year'] >= 1920
    extra = ''
    if pid == 'dorothy-m-tellas': extra = ' The calendar also has a marriage entry for “Dorothy M Tellas” dated 1918, three years after her 1915 birth, so one of the two is wrong.'
    if pid == 'zella-ewell': extra = ' The “Tellas/Jordan” form suggests she married twice.'
    person(pid, nm, ln, by, yr(dd) if dd is not None else '', ix, sex, conf='uncertain',
           note='A Tellas name in the book’s calendar with no parents or spouse given in the repo’s copy of the book data. Unplaced until the book’s genealogy section is checked.' + extra + (' ' + POSS if living else ''), living=living)
person('inf-edward-florence', 'Infant of Edward & Florence Tellas (1928)', 'Tellas', yr(165), '', (165,), '', 'edward-f-tellas', 'florence-tellas', conf='uncertain', note='The calendar entry reads “n. Edward & Florence Tellas,” a 1928 birth. The “n.” is probably a garbled “inf.”', living=False)
person('elizabeth-hall', 'Elizabeth Hall Tellas', 'Hall', '', '', (133,), 'F', conf='uncertain', note='Only a 1914 marriage entry, with no husband named.')
person('george-f-tellas', 'George F. Tellas', 'Tellas', yr(184), yr(157), (184, 157, 84), 'M', conf='uncertain',
       note='Born October 1896, died 1959, married Clara in 1920. Not placed.',
       conflict='He cannot be Charlie and Sarah’s son: William McKinley was born to them on 1 January 1897, three months after George’s October 1896 birth. He may be a son of Jerry or of John II.')
person('clara-wolsiffer', 'Clara P. Wolsiffer Tellas', 'Wolsiffer', yr(156), yr(183), (156, 183, 84), 'F', conf='uncertain', note='Probably the Clara of “George & Clara Tellas” (1920). The calendar gives that bride no maiden name.')
person('matthew-tellas-other', 'Matthew Tellas (son of Charles Frank)', 'Tellas', '', '', (), 'M', 'charles-frank-tellas', None, [claim('other-matthew')], 'likely', 'book', 'The “other Matthew Tellas” of book entry 1263 is Matt’s second cousin once removed. He is living, so his name only.', living='yes')
person('charles-frank-tellas', 'Charles Frank Tellas', 'Tellas', '', '', (), 'M', 'frank-garrett-tellas', None, [claim('other-matthew')], 'likely', 'book', 'Son of Frank Garrett Tellas, per book entry 1263. Presumed living, so his name only. The CLAIMS note links him only tentatively (“probably”) to a 1990 patent. That is not repeated here.', living='yes')

# ---------------- Chillas ----------------
person('johnny-chillas', 'John "Johnny" Chillas', 'Chillas', '', '1884', (), 'M', 'david', 'anna',
       [story('sarah', 'Her brother Johnny was killed in 1884 by a gun accident her future husband witnessed.'), claim('kansas')], 'likely', 'book',
       'Sarah’s brother, killed in 1884 when a gun he was loading went off. Charlie Tellas witnessed it and wrote an account for the sheriff. His parents are taken from Sarah’s record, since he is called her brother. His birth year is not given.')

# ---------------- Godert ----------------
person('fred-godert', 'J. Frederich "Fred" Godert', 'Godert', '', yr(226), (226,), 'M', 'w26999715', 'weurigh', [claim('godert-brothers'), clip('Godert-3', 'Fred Godert, the family records say, was killed at Stones River on the last day of 1862')],
       'likely', 'conflict', 'Margaret Godert’s brother, of Co. F, 37th Indiana. Unmarried.',
       conflict='The calendar dates his death 28 December 1862. The book claim says 31 December 1862, the first day of Stones River. His death there rests on the book alone; it is not confirmed online.')
person('george-godert', 'John George Godert', 'Godert', '', '1864-05-27', (), 'M', 'w26999715', 'weurigh', [claim('godert-brothers')], 'confirmed', 'confirmed',
       'Margaret’s brother George, Co. F, 37th Indiana. He was killed near Dallas, Georgia (Pumpkinvine Creek), on 27 May 1864. The full date is used because the Indiana Adjutant General report confirms it independently. That report lists him as “John G. Godert, recruit.”')
person('anna-godert', 'Anna Godert Tholke', 'Godert', '', yr(26), (26, 51), 'F', conf='uncertain', note='Born a Godert; married Henry Tholke in 1871 (the entry adds “or June 21”); died 1875. Probably one of Johann and Margaret’s nine children, but not stated.')
person('henry-tholke', 'Henry Tholke', 'Tholke', '', '', (51,), 'M', conf='uncertain', note='Husband of Anna Godert, married 1871 per the calendar.')
person('mary-godert', 'Mary Godert Johnson', 'Godert', '', yr(9), (9, 117, 118), 'F', conf='uncertain', note='Born a Godert; married William P. Johnson; died 1921. Probably a daughter of Johann and Margaret, but not stated.',
       conflict='The calendar has two entries for her marked as marriages, one in 1849 and one in 1869 (“William P & Mary (Godert) Johnson”). The 1849 entry carries her name alone, so it is probably her birth.')
person('william-p-johnson', 'William P. Johnson', 'Johnson', '', '', (118,), 'M', conf='likely', note='Husband of Mary Godert, married 1869.')
person('william-h-godert-1840', 'William H. Godert (d. 1840)', 'Godert', '', yr(123), (123,), 'M', conf='uncertain', note='A William H. Godert who died in 1840, probably a child of Johann and Margaret, who married in 1835. Not stated. A second William H. Godert died in 1888, which fits a family reusing a dead child’s name.')
person('william-h-godert-1888', 'William H. Godert (d. 1888)', 'Godert', '', yr(162), (162, 152), 'M', conf='uncertain', note='Died 1888. Probably the William of “William & Mary Godert,” married 1862. Probably a son of Johann and Margaret, but not stated.')
person('mary-wife-godert', 'Mary Godert (wife of William)', 'Godert', '', '', (152,), 'F', conf='uncertain', note='Known only from the 1862 marriage entry “William & Mary Godert.”')
person('garrett-falderman', 'Garrett Falderman', 'Falderman', '', '', (), 'M', src=[claim('weurigh-origin'), story('weurigh', 'She first married Garrett Falderman, and they had a son, Barnet, in 1831… never saw Garrett again.')], conf='likely', note='Margaret Weurigh’s first husband. His fate is unknown.')
person('barnet-falderman', 'Barnet H. Falderman', 'Falderman', yr(161), yr(212), (161, 212, 85), 'M', 'garrett-falderman', 'weurigh', [claim('weurigh-origin')], 'likely', 'book',
       'Margaret Weurigh’s son by Garrett Falderman, born 1831, per the book. The calendar’s “Barnet fl Falderman” (born 1831, OCR noise) and “Barnet H Falderman” (died 1901) are merged. He married Nancy in 1860.')
person('nancy-falderman', 'Nancy Falderman', 'Falderman', '', '', (85,), 'F', conf='likely', note='Wife of Barnet Falderman, married 1860. No maiden name.')
person('frank-g-falderman', 'Frank G. Falderman', 'Falderman', yr(192), yr(225), (192, 225, 132), 'M', conf='uncertain',
       note='Born 1868, died 1915. Probably Annie Tellas’s husband: the calendar’s “Frank & Anna Falderman” (1901) entry is marked as a death but is a couple, so most likely a marriage. Possibly Barnet’s son, but not stated.')
person('charles-bailey', 'Charles Bailey', 'Bailey', '', '', (1,), 'M', conf='uncertain', note='From the 1893 marriage “Charles & Anna Bailey.” The bride may be Annie Tellas, whose death is recorded as “Anna (Tellas) Bailey/Falderman,” but she would have been 17. Unconfirmed.')
person('samuel-bailey-1', 'Samuel T. Bailey I', 'Bailey', yr(53), yr(142), (53, 142, 158, 168), 'M', conf='uncertain',
       note='Born 1894, died 1963. Married Anne Ward in 1917 and Alma in 1934. Probably a son of Charles and Anna Bailey (and so possibly the soldier son for whom Annie Tellas was barred from Army nursing), but not stated.')
person('anne-ward', 'Anne Ward Bailey', 'Ward', yr(2), yr(187), (2, 187, 158), 'F', conf='likely', note='Wife of Samuel T. Bailey I, married 1917.')
person('alma-bailey', 'Alma Bailey', 'Bailey', '', '', (168,), 'F', conf='uncertain', note='Second wife of Samuel T. Bailey I, married 1934. No maiden name or dates.')
person('samuel-bailey-2', 'Samuel T. Bailey II', 'Bailey', '', '', (115,), 'M', conf='uncertain', note='Only a 1935 marriage entry. By the name, a son of Samuel T. I, but not stated.')
person('john-w-bailey', 'John W. Bailey', 'Bailey', yr(14), yr(55), (14, 55), 'M', conf='uncertain', note='Born 1896, died 1897. Probably a child of Charles and Anna Bailey, but not stated.')

# ---------------- Swango ----------------
person('henry-swango-1', 'Henry E. Swango I', 'Swango', yr(52), yr(88), (52, 88, 207), 'M', conf='likely', note='Husband of Alice Tellas, married November 1892 per the calendar.')
person('henry-swango-2', 'Henry E. Swango II', 'Swango', yr(63), yr(170), (63, 170), 'M', conf='uncertain', note='Born 1906, died 1908. By the name, probably a son of Henry I and Alice, but not stated.')
for pid, nm, b, dd, sex in [('roy-t-swango', 'Roy T. Swango', None, 96, 'M'), ('roy-c-swango', 'Roy C. Swango', 38, 109, 'M'), ('andrew-swango', 'Andrew I. Swango', None, 61, 'M'),
                            ('paul-swango', 'Paul C. Swango', 149, 138, 'M'), ('phyllis-swango', 'Phyllis Swango', None, 119, 'F'),
                            ('dolores-swango', 'Dolores F. Swango', 175, None, 'F'), ('vivian-swango', 'Vivian Swango', 193, None, 'F'), ('charles-i-swango', 'Charles I. Swango', 219, None, 'M')]:
    ix = tuple(i for i in (b, dd) if i is not None); living = dd is None
    person(pid, nm, 'Swango', yr(b) if b is not None else '', yr(dd) if dd is not None else '', ix + ((159,) if pid == 'roy-t-swango' else ()), sex, conf='uncertain',
           note='A Swango in the book’s calendar, most likely a descendant of Henry E. Swango I and Alice Tellas. No parents are given.' + (' Married “F Ethel” in 1915.' if pid == 'roy-t-swango' else '') + (' ' + POSS if living else ''), living=living)
person('ethel-thackery', 'F. Ethel Thackery Swango', 'Thackery', yr(47), '', (47, 159), 'F', conf='uncertain', note='Born a Thackery in 1897; probably the “F Ethel” who married Roy T. Swango in 1915. She may be one of John Franklin Thackery and Ida Price’s six or more children, but that is not stated.')
person('charles-h-swango', 'Charles H. Swango', 'Swango', '', '', (87,), 'M', conf='uncertain', note='Only a 1933 marriage entry, “Charles H & Ethel Swango.” That Ethel need not be Ethel Thackery.')
person('margaret-swango', 'Margaret Swango McDermott', 'Swango', yr(174), '', (174, 166), 'F', conf='uncertain', note='Born a Swango in 1899, so probably a daughter of Henry I and Alice, but not stated. Married Elmer J. McDermott in 1921; the entry reads “Elmer S. Margaret McDermott,” OCR for “&”.')
person('elmer-mcdermott', 'Elmer J. McDermott', 'McDermott', yr(79), yr(40), (79, 40, 166), 'M', conf='likely', note='Husband of Margaret Swango, married 1921.')
person('betty-mcdermott', 'Betty McDermott', 'McDermott', yr(27), yr(50), (27, 50), 'F', conf='uncertain', note='Born 1925, died 1927. Probably a child of Elmer and Margaret, but not stated.')
person('faye-chitwood', 'Faye E. Swango Chitwood', 'Swango', yr(58), '', (58, 82), 'F', conf='likely', note='Wife of Allen Chitwood. The entry “Allen & Faye (Swango) Chitwood” gives her maiden name. Born 1918; no death date found.')
person('allen-chitwood', 'Allen Chitwood', 'Chitwood', yr(197), yr(76), (197, 76, 82), 'M', conf='likely', note='Husband of Faye Swango.')
person('inf-chitwood-1938', 'Infant of Allen & Faye Chitwood (1938)', 'Chitwood', '', yr(82), (82,), '', 'allen-chitwood', 'faye-chitwood', conf='likely', note='The calendar entry reads “n. Allen & Faye (Swango) Chitwood,” a death in 1938. The parents are named in the entry.')

# ---------------- Teke / Veit ----------------
person('lewis-teke', 'Lewis Teake (Teke)', 'Teke', '', '', (), 'M', src=[claim('name-origin'), claim('lena')], conf='likely', note='Lena Hunterman’s first husband, married 1842. John I took his surname as a boy. What became of him after about 1853 is unknown.')
person('william-e-teke', 'William Everett Teke', 'Teke', '', yr(106), (106, 75), 'M', 'lewis-teke', 'helena', [claim('sheriff'), story('helena', 'They had three more children, including William Teke, who became sheriff of Dearborn County.')],
       'confirmed', 'conflict', 'John I’s half-brother. The county officers list confirms he was Dearborn County sheriff, 1896–98. He died in office.',
       conflict='The calendar dates his death 18 June 1898. The book claim says 20 June 1898.')
person('wilhelmina-teke', 'Wilhelmina Teke', 'Teke', '', '', (75,), 'F', conf='likely', note='Wife of William E. Teke, named in the 1879 infant entry.')
person('inf-teke-1879', 'Infant of William & Wilhelmina Teke (1879)', 'Teke', yr(75), '', (75,), '', 'william-e-teke', 'wilhelmina-teke', conf='uncertain', note='The calendar entry reads “n. William & Wilhelmina Teke,” a birth in 1879. The “n.” is probably a garbled “inf.”')
person('louis-h-teke', 'Louis H. Teke', 'Teke', yr(104), yr(186), (104, 186), 'M', conf='uncertain', note='Born 1847, after Lena married Lewis Teake in 1842, so he may be one of their three children, but not stated.')
person('margaret-luker', 'Margaret M. Luker Teke', 'Luker', '', yr(208), (208,), 'F', conf='uncertain', note='Died 1909. Married into the Teke family; her husband is not named.')
person('louis-veit', 'Louis Veit', 'Veit', yr(91), yr(216), (91, 216, 89), 'M', src=[story('helena', 'she married Louis Veit, a Hanover-born hotel and saloon keeper')], conf='likely', note='Lena’s second husband, a Hanover-born hotel and saloon keeper. After her death in 1876 he married Margaret Transier (1877).')
person('margaret-transier', 'Margaret Transier Veit', 'Transier', '', yr(176), (176, 89), 'F', conf='likely', note='Second wife of Louis Veit, married 1877.')
person('george-veit', 'George Veit', 'Veit', yr(66), yr(172), (66, 172), 'M', conf='uncertain', note='Born 1864, died 1866. Probably a child of Louis Veit, but not stated. Lena would have been 45.')

# ---------------- Thackery ----------------
person('eileen-anderson', 'D. Eileen Anderson Thackery', 'Anderson', yr(18), yr(20), (18, 20), 'F', conf='uncertain', note='Born 1929, died 1990. Married into the Thackery family; her husband is not named.')

# ---------------- Fratzke / Heick (obituaries and census, retold in the repo) ----------------
person('janice-fratzke', 'Janice Fratzke', 'Fratzke', '', '', (), 'F', 'wma', 'mae',
       [story('wma', 'Father of Bill and Janice.'), {'t': 'app.js CENSUS[fratzke]: 1950 U.S. Census, Ross Township, ED 45-89, sheet 48, lines 25–28 (William A., Mae, Bill 10, Janice 7)'}],
       'confirmed', 'confirmed', 'Bill’s sister, listed with her parents in the 1950 census. Her age then (7) implies a birth around 1942–43, but no birth date is entered. Her married name is not in the repo. ' + POSS, living=True, topic='Obituary relatives')
person('george-anglin', 'George Anglin', 'Anglin', '', '', (), 'M', src=[story('mae', 'Widowed in 1982, she remarried George Anglin')], conf='likely', verdict='book',
       note='Mae Heick Fratzke’s second husband, from her obituary as retold in STORIES and CLIPPINGS. Whether he is living is unknown.', topic='Obituary relatives')

# ---------------- People in the calendar with no stated tie to any branch ----------------
UNPLACED = [('luanna-newkirk', 'Luanna Newkirk', 4, None), ('benjamin-newkirk', 'Benjamin D. Newkirk', None, 36), ('marlin-newkirk', 'Marlin Newkirk', 189, None),
            ('donald-hadler', 'Donald Hadler', None, 6), ('earl-hadler', 'Earl C. Hadler', 77, None), ('frances-hadler', 'Frances Hadler', 150, None),
            ('daniel-zylov', 'Daniel E. Zylov', None, 7), ('pauline-holtkamp', 'Pauline Holtkamp', 12, None),
            ('loyd-carmichael', 'Loyd Carmichael', 13, None), ('marie-carmichael', 'Marie Carmichael', 17, None),
            ('ruth-guthrie', 'Ruth Guthrie', 15, None), ('ray-guthrie', 'Ray Guthrie', 151, None),
            ('william-redmon', 'William F. Redmon', None, 16), ('frieda-redmon', 'Frieda K. Redmon', 108, None), ('joseph-redmon', 'Joseph Redmon', 146, None),
            ('joseph-e-redmon', 'Joseph E. Redmon', None, 188), ('james-redmon', 'James R. Redmon', None, 210), ('misty-redmon', 'Misty Redmon', None, 131),
            ('donald-griffin', 'Donald L. Griffin', 25, None), ('alice-griffin', 'Alice M. Griffin', 54, None),
            ('donna-ketchum', 'Donna Ketchum', 28, None), ('charles-ketchum', 'Charles H. Ketchum', 215, None),
            ('margaret-jordan', 'Margaret M. Jordan', 39, None), ('clarence-jordan', 'Clarence G. Jordan', 60, 223),
            ('margie-maurer', 'Margie M. Maurer', 57, None), ('francis-maurer', 'Francis W. Maurer', 143, None), ('robert-maurer', 'Robert Maurer', None, 124),
            ('james-wuerth', 'James W. Wuerth', 59, None),
            ('harrell-aldrich', 'C. Harrell Aldrich', 137, 65), ('walter-aldrich', 'Walter Aldrich', None, 136), ('walter-d-aldrich', 'Walter D. Aldrich', None, 144),
            ('maurice-desseyn', 'Maurice H. Desseyn', 67, None), ('donald-desseyn', 'Donald Desseyn', None, 130),
            ('richard-herrold', 'Richard E. Herrold', 182, None), ('wilma-hillman', 'Wilma G. Hillman', 160, None), ('rita-truax', 'Rita J. Truax', 163, None),
            ('irene-robbins', 'C. Irene Robbins', 221, None), ('james-robbins', 'L. James Robbins', 206, None), ('timothy-robbins', 'Timothy Robbins', None, 179),
            ('dale-baker', 'C. Dale Baker', 195, None), ('luella-baker', 'A. Luella Baker', 209, None),
            ('franklin-jones', 'Franklin D. Jones', 203, 169), ('john-d-jones', 'John D. Jones', None, 127),
            ('evelyn-dodds', 'Evelyn Dodds', 101, None), ('rollin-dodds', 'Rollin Dodds', 147, None),
            ('gregory-williams', 'Gregory C. Williams', None, 153), ('robert-thomas', 'Robert Thomas', None, 126), ('lawson-allen', 'Lawson Allen', None, 120)]
for pid, nm, b, dd in UNPLACED:
    ix = tuple(i for i in (b, dd) if i is not None); living = dd is None
    extra = ''
    if pid == 'evelyn-dodds': extra = ' The calendar spells it “Eveiyn,” taken as OCR for Evelyn.'
    if pid == 'wilma-hillman': extra = ' Hillman is the book author’s surname, so she may be his relative.'
    if pid == 'marlin-newkirk' or pid == 'luanna-newkirk': extra = ' Benjamin D. Newkirk (d. 1990) may be a parent; not stated.'
    person(pid, nm, nm.split()[-1], yr(b) if b is not None else '', yr(dd) if dd is not None else '', ix, '', conf='uncertain',
           note='In the book’s calendar, so a descendant of John I and Margaret or a spouse of one, but the repo’s copy of the book data gives no parents or spouse.' + extra + (' ' + POSS if living else ''), living=living, topic='Unplaced')
# Couples with no dates beyond the event
for pid, nm, ix, ln in [('william-jones', 'William Jones', 134, 'Jones'), ('larry-gray', 'Larry Gray', 125, 'Gray'), ('carol-gray', 'Carol Gray', 125, 'Gray'),
                        ('ruth-herrold', 'Ruth Herrold', 69, 'Herrold')]:
    person(pid, nm, ln, '', '', (ix,), '', conf='uncertain', note='Known only from a couple entry in the calendar' + (' (“Larry & Carol Gray,” 1966, marked as a death but probably a marriage).' if 'gray' in pid else ' (“n. Richard & Ruth Herrold,” an infant who died in 1984).' if pid == 'ruth-herrold' else ' (marriage, 1932).') + ' ' + POSS, living=True, topic='Unplaced')
person('inf-herrold-1984', 'Infant of Richard & Ruth Herrold (1984)', 'Herrold', '', yr(69), (69,), '', 'richard-herrold', 'ruth-herrold', conf='uncertain', note='The calendar entry reads “n. Richard & Ruth Herrold,” a death in 1984. The parents are named in the entry. Only the death year is kept.', topic='Unplaced')

# ---------------- relationships (spouses, and parent links the sources suggest but do not state) ----------------
C = cal
for a, b, ix, conf in [('john2', 'sophia-link', 3, 'likely'), ('jerry', 'rosa-spangler', 217, 'likely'), ('ray-tellas', 'elizabeth-ray', 198, 'likely'),
                       ('william-t-tellas', 'anna-pieper', 71, 'likely'), ('john-louis-tellas', 'anna-herbert', 92, 'uncertain'), ('john-louis-tellas', 'mabel-black', 181, 'uncertain'),
                       ('thomas-f-tellas', 'clara-koebbe', 121, 'likely'), ('frank-garrett-tellas', 'elizabeth-frank', 148, 'likely'), ('walter-thackery', 'anna-tellas-thackery', 80, 'likely'),
                       ('george-f-tellas', 'clara-wolsiffer', 84, 'uncertain'), ('henry-swango-1', 'alice-tellas', 207, 'likely'), ('frank-g-falderman', 'annie-tellas', 132, 'uncertain'),
                       ('charles-bailey', 'annie-tellas', 1, 'uncertain'), ('samuel-bailey-1', 'anne-ward', 158, 'likely'), ('samuel-bailey-1', 'alma-bailey', 168, 'likely'),
                       ('henry-tholke', 'anna-godert', 51, 'likely'), ('william-p-johnson', 'mary-godert', 118, 'likely'), ('william-h-godert-1888', 'mary-wife-godert', 152, 'likely'),
                       ('barnet-falderman', 'nancy-falderman', 85, 'likely'), ('roy-t-swango', 'ethel-thackery', 159, 'uncertain'), ('elmer-mcdermott', 'margaret-swango', 166, 'likely'),
                       ('allen-chitwood', 'faye-chitwood', 82, 'likely'), ('william-e-teke', 'wilhelmina-teke', 75, 'likely'), ('louis-veit', 'margaret-transier', 89, 'likely'),
                       ('dale-baker', 'luella-baker', 224, 'likely'), ('larry-gray', 'carol-gray', 125, 'uncertain'), ('richard-herrold', 'ruth-herrold', 69, 'likely'),
                       ('edward-f-tellas', 'florence-tellas', 165, 'likely')]:
    rel('spouse', a, b, conf, 'Couple named together in one calendar entry.' + (' The bride’s identification with this person is an inference.' if conf == 'uncertain' else ''), [C(ix)], date=str(E[ix]['year']) if E[ix]['type'] == 'm' else '')
rel('spouse', 'garrett-falderman', 'weurigh', 'likely', 'Margaret Weurigh’s first marriage, per the book.', [claim('weurigh-origin')], date='')
rel('spouse', 'lewis-teke', 'helena', 'likely', 'Married 1842, per the book.', [claim('lena')], date='1842')
rel('spouse', 'louis-veit', 'helena', 'likely', 'Lena’s second marriage, in the 1850s, per the book.', [claim('lena')], date='')
rel('spouse', 'george-anglin', 'mae', 'likely', 'Mae’s second marriage, after 1982, from her obituary as retold in the repo.', [story('mae', 'Widowed in 1982, she remarried George Anglin')], date='')
SUGGEST = [('john1', 'dora-tellas'), ('john1', 'alice-tellas'), ('john1', 'margaret-may-tellas'), ('john1', 'william-t-tellas'),
           ('henry-swango-1', 'henry-swango-2'), ('henry-swango-1', 'margaret-swango'), ('samuel-bailey-1', 'samuel-bailey-2'), ('charles-bailey', 'samuel-bailey-1'),
           ('charles-bailey', 'john-w-bailey'), ('elmer-mcdermott', 'betty-mcdermott'), ('lewis-teke', 'louis-h-teke'), ('louis-veit', 'george-veit'),
           ('w26999715', 'anna-godert'), ('w26999715', 'mary-godert'), ('w26999715', 'william-h-godert-1840'), ('w26999715', 'william-h-godert-1888'), ('jfrank', 'ethel-thackery')]
for a, b in SUGGEST:
    rel('parent-suggested', a, b, 'uncertain', 'Suggested by surname, a “II” suffix or dates only. No passage in the repo states it, so it is NOT set in father/mother. Check against the book’s genealogy section before linking.', [], stated=False, verdict='open')

# ---------------- dedupe log: calendar entries matched to people already in the tree ----------------
MERGED = [('charles', (19, 180, 94), 'Calendar has birth 23 Jan 1868 and death 27 Sep 1942; the tree has 24 Jan and 28 Sep. Marriage 1 Jun 1891 against 3 Jun 1891 in the book claim.'),
          ('wmck', (0, 86), 'Birth and death agree with the tree.'),
          ('john1', (31, 214), 'Death agrees. Marriage 2 Dec 1864 against 1 Dec in the book and 30 Nov in the Bible note.'),
          ('margodert', (194, 70), 'Death 30 Mar 1905 against 31 Mar in the tree. Birth agrees.'),
          ('weurigh', (32, 49, 97), 'Birth and death agree. Marriage dated 5 June 1835, “or June 7th”.'),
          ('helena', (171, 199), 'Birth 13 Sep 1818 against 12 Sep in the tree. Death agrees.'),
          ('sarah', (178, 202), 'Birth 24 Sep and death 8 Nov 1955, against 25 Sep and 10 Nov in the tree.'),
          ('w26999715', (185, 105, 97), '“John E Godert” is Johann Godert. Birth 9 Oct and death 13 Jun 1879, against 10 Oct and 14 Jun.')]
dedupe = [{'existing': pid, 'name': TREE[pid]['name'], 'calendarEntries': [ev(i) for i in ix], 'note': n} for pid, ix, n in MERGED]

# integrity checks
ids = [p['id'] for p in people]; assert len(ids) == len(set(ids))
allids = set(ids) | set(TREE)
for p in people:
    for k in ('father', 'mother'): assert p[k] is None or p[k] in allids, (p['id'], p[k])
for r in rels: assert r['a'] in allids and r['b'] in allids, r
ABOUT = ('Collateral relatives staged for review, not yet loaded by the site. Built only from book and obituary material already in this repo '
         '(app.js EVENTS calendar, CLAIMS, STORIES, CLIPPINGS, CENSUS). The full book scan and obituary text captures are not in the repo. '
         'Person records follow the EXTRA schema in app.js. father/mother are set only where a source passage names the parent. '
         'Calendar dates are reduced to the year (see notes.json). Living or possibly-living people: name and year only, no contact details.')
json.dump({'_about': ABOUT, 'people': people}, open(os.path.join(OUT, 'people.json'), 'w'), ensure_ascii=False, indent=1)
json.dump({'_about': 'Spouse links (the person schema has no spouse field) and parent links that are suggested but not stated. Only links with statedInSource=true should be loaded as-is.', 'relationships': rels}, open(os.path.join(OUT, 'relationships.json'), 'w'), ensure_ascii=False, indent=1)
json.dump({'_about': 'Fact-check notes in the CLAIMS style: one per added person, with source passage, verdict (CLAIMS vocabulary), confidence (confirmed / likely / uncertain) and any conflict. dedupe lists calendar entries matched to people already in the tree.',
           'notes': notes, 'dedupe': dedupe}, open(os.path.join(OUT, 'notes.json'), 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(people), 'people;', len(rels), 'relationships;', len(dedupe), 'dedupe')
print(Counter(n['confidence'] for n in notes), Counter(r['type'] for r in rels))
print('possibly living:', sum(1 for n in notes if n.get('possiblyLiving')), 'conflicts:', sum(1 for n in notes if n.get('conflict')))
print('linked parents:', sum(1 for p in people if p['father'] or p['mother']))
# calendar coverage
covered = set()
for n in notes:
    for s in n['sources']:
        for m in re.finditer(r'\(“(.*?)”\)', s['t']): covered.add(m.group(1))
for x in dedupe:
    for c in x['calendarEntries']: covered.add(re.search(r'\(“(.*?)”\)', c).group(1))
for r in rels:
    for s in r['sources']:
        for m in re.finditer(r'\(“(.*?)”\)', s['t']): covered.add(m.group(1))
miss = sorted(set(e['who'] for e in E) - covered)
LEFT_OUT = {'C Matthew & Deborah Collins'}  # a 1987 couple entry: almost certainly living, name only, no tie to any branch
assert set(miss) == LEFT_OUT, miss
print('calendar names deliberately left out:', miss)
