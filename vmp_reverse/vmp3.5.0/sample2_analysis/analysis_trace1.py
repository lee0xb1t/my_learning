
import matplotlib.pyplot as plt
import pandas as pd
from d3blocks import D3Blocks


lines = []
bbls = []

with open("sample2_bbl.trace1", "r", encoding="utf-8") as file:
    __lines = file.readlines()
    for line in __lines:
        if '=========' in line:
            break
        lines.append(line.replace('\n', ''))

for line in lines:
    bbl_item = line.split(',')
    start_addr = bbl_item[0].split(':')[1]
    target_addr = bbl_item[2].split(':')[1]
    bbls.append(
        {
            'start': start_addr,
            'target': target_addr,
        }
    )

# g = ig.Graph()

# all_vertices = set()
# for bbl in bbls:
#     all_vertices.add(bbl['start'])
#     all_vertices.add(bbl['target'])

# g.add_vertices(list(all_vertices))

# names = []
# i = 0

# for bbl in bbls:
#     print(i, (bbl['start'], bbl['target']))
#     g.add_edges([(bbl['start'], bbl['target'])])
#     i+=1

# g.vs["name"] = names

# print(names)

# layout = g.layout('kk')

# fig, ax = plt.subplots(figsize=(8, 6))
# ig.plot(g, layout=layout, target=ax)

# # g.vs["label"] = g.vs["name"]
# # # color_dict = {"m": "blue", "f": "pink"}
# # # g.vs["color"] = [color_dict[gender] for gender in g.vs["gender"]]
# # ig.plot(g, layout=layout, bbox=(300, 300), margin=20)  # Cairo backend
# # ig.plot(g, layout=layout, target=ax)  # matplotlib backend

# # plt.show()


bbls_dict = {}
named_bbls = []

i = 0
for bbl in bbls:
    if bbl['start'] not in bbls_dict:
        bbls_dict[bbl['start']] = 'BBL'+str(i)
        i+=1
for bbl in bbls:
    if bbl['target'] not in bbls_dict:
        bbls_dict[bbl['target']] = 'BBL'+str(i)
        i+=1

i=0
for bbl in bbls:
    named_bbls.append({
        'source': bbls_dict[bbl['start']],
        'target': bbls_dict[bbl['target']],
        'source_addr': hex(int(bbl['start'])),
        'target_addr': hex(int(bbl['target'])),
        'id': i
    })
    i+=1
    

## Output BBL
# for named_bbl in named_bbls:
#     if named_bbl['source'] == 'BBL175':
#         print(named_bbl)
# for named_bbl in named_bbls:
#     if named_bbl['target'] == 'BBL175':
#         print(named_bbl)

# for i in range(9):
#     for named_bbl in named_bbls:
#         if named_bbl['source'] == 'BBL'+str(176+i):
#             print(named_bbl)
#             break
# f = open('analysis_trace.out', 'w')
# for named_bbl in named_bbls:
#     print(named_bbl)
#     f.write(str(named_bbl))
#     f.write('\n')
# f.close()

bbl_count = {}
# 统计target出现次数最多的基本块
for named_bbl in named_bbls:
    target = named_bbl['target']
    if target not in bbl_count:
        bbl_count[target] = 1
    else:
        bbl_count[target] += 1
bbl_count = dict(sorted(bbl_count.items(), key=lambda item: item[1], reverse=True))
# for k in bbl_count:
#     print(k, ':', bbl_count[k])
f = open('count_target_trace1.txt', 'w')
for k in bbl_count:
    f.write(f"{k}:{bbl_count[k]}\n")
f.close()


tooltip_data = []
for named_bbl in named_bbls:
    tooltip_data.append(
        f"Source: {named_bbl['source_addr']}<br>Target: {named_bbl['target_addr']}"
    )

data = []
i=0
for named_bbl in named_bbls:
    data.append({
        'source': named_bbl['source'],
        'target': named_bbl['target'],
        'weight': i+1,
    })
    i+=1


#-----------------------------------------------------------------
# df = pd.DataFrame(data, columns=['source', 'target', 'weight'])

# d3 = D3Blocks()
# d3.d3graph(df)

# d3.set_node_properties(tooltip=tooltip_data,)
# d3.set_edge_properties(directed=True)

# d3.show()
