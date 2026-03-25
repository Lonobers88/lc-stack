"""
title: Redux PC Prijszoeker
author: LocalCompute
description: Zoekt prijzen van alle Redux Gaming producten: gaming PCs, accessoires, controllers, muizen, toetsenborden, headsets, monitoren, muismatten en abonnementen. Gebruik zoek_pc_prijs voor PC's en zoek_product_prijs voor alle overige producten.
"""

PRODUCTS_DATA = """Model: Nighthawk - RX 9060 XT 16GB Prime | SKU: RNH-INTEL-R97XT | CPU: Intel Core Ultra 7 265K | GPU: RX 9060 XT 16GB Prime | RAM: 48GB DDR5 G.Skill Trident Z5 Neo RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3229 | Voorraad: 0

Model: Nighthawk - RTX 5070 12GB Prime | SKU: RNH-INTEL-N57 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 12GB Prime | RAM: 48GB DDR5 G.Skill Trident Z5 Neo RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3499 | Voorraad: 0

Model: Nighthawk - RTX 5070 Ti 16GB Prime | SKU: RNH-INTEL-N57T | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 Ti 16GB Prime | RAM: 48GB DDR5 G.Skill Trident Z5 Neo RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3949 | Voorraad: 0

Model: Nighthawk - RTX 5080 16GB Prime | SKU: RNH-INTEL-N58 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5080 16GB Prime | RAM: 48GB DDR5 G.Skill Trident Z5 Neo RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4399 | Voorraad: 0

Model: ProArt Ultimate - RTX 5080 16GB ProArt | SKU: RUWS-AMD-N58 | CPU: AMD Ryzen 9 9950X | GPU: RTX 5080 16GB ProArt | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 EVO Plus | Actieprijs: EUR 5479 | Voorraad: 0

Model: ProArt Ultimate - RTX 5070 Ti 16GB Prime | SKU: RUWS-INTEL-N57T | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 Ti 16GB Prime | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 EVO Plus | Actieprijs: EUR 4649 | Voorraad: 0

Model: ProArt Ultimate - RTX 5080 16GB ProArt | SKU: RUWS-INTEL-N58 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5080 16GB ProArt | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 EVO Plus | Actieprijs: EUR 5579 | Voorraad: 0

Model: Supernova - RTX 5060 8GB TUF | SKU: RSN-INTEL-N56 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5060 8GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 2449 | Voorraad: 0

Model: Supernova - RTX 5060 Ti 8GB TUF | SKU: RSN-INTEL-N56T8 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5060 Ti 8GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 2599 | Voorraad: 0

Model: Prism - RTX 5060 8GB Prime | SKU: PRISM-INTEL-N56 | CPU: Intel Core i7 14700F | GPU: RTX 5060 8GB Prime | RAM: 32GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2199 | Voorraad: 0

Model: Nova - RTX 5060 Ti 8GB Dual | SKU: NOVA-AMD-N56T8 | CPU: AMD Ryzen 5 7500F | GPU: RTX 5060 Ti 8GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1779 | Voorraad: 2

Model: NoaNoella - RTX 5070 Ti 16GB TUF White | SKU: RDX-NN-AMD-N57T | CPU: AMD Ryzen 7 9800X3D | GPU: RTX 5070 Ti 16GB TUF White | RAM: 32GB DDR5 Kingston Fury Beast RGB White | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3899 | Voorraad: 0

Model: ProArt Ultimate - RTX 5070 Ti 16GB Prime | SKU: RUWS-AMD-N57T | CPU: AMD Ryzen 9 9900X | GPU: RTX 5070 Ti 16GB Prime | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 EVO Plus | Actieprijs: EUR 4679 | Voorraad: 0

Model: ProArt Ultimate - RTX 5090 32GB TUF | SKU: RUWS-AMD-N59 | CPU: AMD Ryzen 9 9950X | GPU: RTX 5090 32GB TUF | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 EVO Plus | Actieprijs: EUR 7349 | Voorraad: 0

Model: ProArt Ultimate - RTX 5090 32GB TUF | SKU: RUWS-INTEL-N59 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5090 32GB TUF | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 EVO Plus | Actieprijs: EUR 7449 | Voorraad: 0

Model: Hatsune Miku - RTX 5080 16GB Astral Hatsune Miku | SKU: HATSUNE-AMD-N58 | CPU: AMD Ryzen 7 9850X3D | GPU: RTX 5080 16GB Astral Hatsune Miku | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 5699 | Voorraad: 1

Model: Hyperion - RTX 5080 16GB Astral | SKU: ROGH-INTEL-N58 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5080 16GB Astral | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 Pro | Actieprijs: EUR 6399 | Voorraad: 0

Model: Hyperion - RTX 5080 16GB Astral | SKU: ROGH-AMD-N58 | CPU: AMD Ryzen 9 9950X3D | GPU: RTX 5080 16GB Astral | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 Pro | Actieprijs: EUR 6429 | Voorraad: 0

Model: Hyperion - RTX 5090 32GB Astral | SKU: ROGH-INTEL-N59 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5090 32GB Astral | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 EVO Plus | Actieprijs: EUR 8279 | Voorraad: 0

Model: Hyperion - RTX 5090 32GB Astral | SKU: ROGH-AMD-N59 | CPU: AMD Ryzen 9 9950X3D | GPU: RTX 5090 32GB Astral | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Samsung 990 EVO Plus | Actieprijs: EUR 8279 | Voorraad: 0

Model: ROG Ultimate - RTX 5090 32GB Astral LC | SKU: ROGU-INTEL-N59 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5090 32GB Astral LC | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Kingston Fury Renegade G5 | Actieprijs: EUR 9049 | Voorraad: 0

Model: ROG Ultimate - RTX 5090 32GB Astral LC | SKU: ROGU-AMD-N59 | CPU: AMD Ryzen 9 9950X3D | GPU: RTX 5090 32GB Astral LC | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 4TB Kingston Fury Renegade G5 | Actieprijs: EUR 9079 | Voorraad: 0

Model: TUF Ultimate - RTX 5070 Ti 16GB TUF | SKU: RTU-AMD-N57T | CPU: AMD Ryzen 9 9900X3D | GPU: RTX 5070 Ti 16GB TUF | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4479 | Voorraad: 0

Model: TUF Ultimate - RTX 5080 16GB TUF | SKU: RTU-AMD-N58 | CPU: AMD Ryzen 9 9900X3D | GPU: RTX 5080 16GB TUF | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4979 | Voorraad: 0

Model: TUF Ultimate - RTX 5090 32GB TUF | SKU: RTU-AMD-N59 | CPU: AMD Ryzen 9 9900X3D | GPU: RTX 5090 32GB TUF | RAM: 64GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 6899 | Voorraad: 1

Model: Supernova - RTX 5060 8GB TUF | SKU: RSN-AMD-N56 | CPU: AMD Ryzen 7 7800X3D | GPU: RTX 5060 8GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 2549 | Voorraad: 0

Model: Supernova - RTX 5060 Ti 8GB TUF | SKU: RSN-AMD-N56T8 | CPU: AMD Ryzen 7 7800X3D | GPU: RTX 5060 Ti 8GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 2699 | Voorraad: 0

Model: Supernova - RX 9060 XT 16GB TUF | SKU: RSN-AMD-R96XT | CPU: AMD Ryzen 7 7800X3D | GPU: RX 9060 XT 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 2699 | Voorraad: 1

Model: Supernova - RTX 5060 Ti 16GB TUF | SKU: RSN-INTEL-N56T | CPU: Intel Core Ultra 7 265K | GPU: RTX 5060 Ti 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 2779 | Voorraad: 0

Model: Supernova - RTX 5060 Ti 16GB TUF | SKU: RSN-AMD-N56T | CPU: AMD Ryzen 7 7800X3D | GPU: RTX 5060 Ti 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 2849 | Voorraad: 0

Model: Supernova - RTX 5070 12GB TUF | SKU: RSN-INTEL-N57 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 12GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 2929 | Voorraad: 0

Model: Supernova - RTX 5070 12GB TUF | SKU: RSN-AMD-N57 | CPU: AMD Ryzen 7 7800X3D | GPU: RTX 5070 12GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 2999 | Voorraad: 0

Model: Supernova - RX 9070 16GB TUF | SKU: RSN-AMD-R97 | CPU: AMD Ryzen 7 7800X3D | GPU: RX 9070 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3029 | Voorraad: 0

Model: Supernova - RX 9070 XT 16GB TUF | SKU: RSN-AMD-R97XT | CPU: AMD Ryzen 7 9800X3D | GPU: RX 9070 XT 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3229 | Voorraad: 1

Model: Supernova - RTX 5070 Ti 16GB TUF | SKU: RSN-INTEL-N57T | CPU: Intel Core Ultra 9 285K | GPU: RTX 5070 Ti 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3649 | Voorraad: 0

Model: Supernova - RTX 5070 Ti 16GB TUF | SKU: RSN-AMD-N57T | CPU: AMD Ryzen 7 9800X3D | GPU: RTX 5070 Ti 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3479 | Voorraad: 2

Model: Supernova - RTX 5080 16GB TUF | SKU: RSN-INTEL-N58 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5080 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 4149 | Voorraad: 0

Model: Supernova - RTX 5080 16GB TUF | SKU: RSN-AMD-N58 | CPU: AMD Ryzen 7 9800X3D | GPU: RTX 5080 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3979 | Voorraad: 0

Model: Supernova - RTX 5090 32GB TUF | SKU: RSN-INTEL-N59 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5090 32GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 6079 | Voorraad: 0

Model: Supernova - RTX 5090 32GB TUF | SKU: RSN-AMD-N59 | CPU: AMD Ryzen 7 9800X3D | GPU: RTX 5090 32GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 5929 | Voorraad: 0

Model: Prism - RTX 5060 8GB Prime | SKU: PRISM-AMD-N56 | CPU: AMD Ryzen 7 9700X | GPU: RTX 5060 8GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2279 | Voorraad: 0

Model: Prism - RTX 5060 Ti 8GB Prime | SKU: PRISM-INTEL-N56T8 | CPU: Intel Core i7 14700F | GPU: RTX 5060 Ti 8GB Prime | RAM: 32GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2329 | Voorraad: 0

Model: Prism - RTX 5060 Ti 8GB Prime | SKU: PRISM-AMD-N56T8 | CPU: AMD Ryzen 7 9700X | GPU: RTX 5060 Ti 8GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2379 | Voorraad: 0

Model: Prism - RX 9060 XT 16GB Prime | SKU: PRISM-AMD-R96XT | CPU: AMD Ryzen 7 9700X | GPU: RX 9060 XT 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2399 | Voorraad: 1

Model: Prism - RTX 5060 Ti 16GB Prime | SKU: PRISM-INTEL-N56T | CPU: Intel Core i7 14700F | GPU: RTX 5060 Ti 16GB Prime | RAM: 32GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2499 | Voorraad: 0

Model: Prism - RTX 5060 Ti 16GB Prime | SKU: PRISM-AMD-N56T | CPU: AMD Ryzen 7 9700X | GPU: RTX 5060 Ti 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2579 | Voorraad: 0

Model: Prism White - RTX 5070 12GB Prime White | SKU: PRISM-WH-AMD-N57 | CPU: AMD Ryzen 7 9700X | GPU: RTX 5070 12GB Prime White | RAM: 32GB DDR5 Kingston Fury Beast RGB White | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2829 | Voorraad: 1

Model: Prism - RTX 5070 12GB Prime | SKU: PRISM-INTEL-N57 | CPU: Intel Core i7 14700F | GPU: RTX 5070 12GB Prime | RAM: 32GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2599 | Voorraad: 0

Model: Prism White - RX 9070 XT 16GB Prime White | SKU: PRISM-WH-AMD-R97XT | CPU: AMD Ryzen 7 7800X3D | GPU: RX 9070 XT 16GB Prime White | RAM: 32GB DDR5 Kingston Fury Beast RGB White | SSD: 1TB Kingston NV3 | Actieprijs: EUR 3129 | Voorraad: 0

Model: Prism - RTX 5070 12GB Prime | SKU: PRISM-AMD-N57 | CPU: AMD Ryzen 7 9700X | GPU: RTX 5070 12GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2679 | Voorraad: 0

Model: Prism - RX 9070 16GB Prime | SKU: PRISM-AMD-R97 | CPU: AMD Ryzen 7 9700X | GPU: RX 9070 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2699 | Voorraad: 0

Model: Prism - RX 9070 XT 16GB Prime | SKU: PRISM-AMD-R97XT | CPU: AMD Ryzen 7 7800X3D | GPU: RX 9070 XT 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2979 | Voorraad: 1

Model: Prism - RTX 5070 Ti 16GB Prime | SKU: PRISM-AMD-N57T | CPU: AMD Ryzen 7 7800X3D | GPU: RTX 5070 Ti 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 3279 | Voorraad: 0

Model: Prism - RTX 5070 Ti 16GB Prime | SKU: PRISM-INTEL-N57T | CPU: Intel Core i9 14900F | GPU: RTX 5070 Ti 16GB Prime | RAM: 32GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 3279 | Voorraad: 0

Model: Prism - RTX 5080 16GB Prime | SKU: PRISM-AMD-N58 | CPU: AMD Ryzen 7 7800X3D | GPU: RTX 5080 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 3699 | Voorraad: 0

Model: Prism - RTX 5080 16GB Prime | SKU: PRISM-INTEL-N58 | CPU: Intel Core i9 14900F | GPU: RTX 5080 16GB Prime | RAM: 32GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 3729 | Voorraad: 0

Model: Prism - RTX 5090 32GB TUF | SKU: PRISM-AMD-N59 | CPU: AMD Ryzen 7 7800X3D | GPU: RTX 5090 32GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 5699 | Voorraad: 0

Model: Prism - RTX 5090 32GB TUF | SKU: PRISM-INTEL-N59 | CPU: Intel Core i9 14900F | GPU: RTX 5090 32GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 5899 | Voorraad: 0

Model: Nova Pro - RTX 5060 8GB Dual | SKU: RNP-AMD-N56 | CPU: AMD Ryzen 7 9700X | GPU: RTX 5060 8GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2049 | Voorraad: 0

Model: Nova Pro - RX 9060 XT 16GB Dual | SKU: RNP-AMD-R96XT | CPU: AMD Ryzen 7 9700X | GPU: RX 9060 XT 16GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2179 | Voorraad: 0

Model: Nova Pro - RTX 5060 Ti 16GB Dual | SKU: RNP-AMD-N56T | CPU: AMD Ryzen 7 9700X | GPU: RTX 5060 Ti 16GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2349 | Voorraad: 0

Model: Nova Pro - RTX 5070 12GB Dual | SKU: RNP-AMD-N57 | CPU: AMD Ryzen 7 9700X | GPU: RTX 5070 12GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2449 | Voorraad: 0

Model: Nova Pro - RX 9070 16GB Prime | SKU: RNP-AMD-R97 | CPU: AMD Ryzen 7 9700X | GPU: RX 9070 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2529 | Voorraad: 0

Model: Nova Pro - RX 9070 XT 16GB Prime | SKU: RNP-AMD-R97XT | CPU: AMD Ryzen 7 9700X | GPU: RX 9070 XT 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2679 | Voorraad: 0

Model: Nova Pro - RTX 5070 Ti 16GB Prime | SKU: RNP-AMD-N57T | CPU: AMD Ryzen 7 9700X | GPU: RTX 5070 Ti 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2949 | Voorraad: 0

Model: Nova Pro - RTX 5080 16GB Prime | SKU: RNP-AMD-N58 | CPU: AMD Ryzen 7 9700X | GPU: RTX 5080 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 3399 | Voorraad: 0

Model: Nova Pro - RTX 5060 8GB Dual | SKU: RNP-INTEL-N56 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5060 8GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2029 | Voorraad: 0

Model: Nova Pro - RX 9060 XT 16GB Dual | SKU: RNP-INTEL-R96XT | CPU: Intel Core Ultra 7 265K | GPU: RX 9060 XT 16GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2129 | Voorraad: 0

Model: Nova Pro - RTX 5060 Ti 16GB Dual | SKU: RNP-INTEL-N56T | CPU: Intel Core Ultra 7 265K | GPU: RTX 5060 Ti 16GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2329 | Voorraad: 0

Model: Nova Pro - RTX 5070 12GB Dual | SKU: RNP-INTEL-N57 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 12GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2399 | Voorraad: 0

Model: Nova Pro - RX 9070 16GB Prime | SKU: RNP-INTEL-R97 | CPU: Intel Core Ultra 7 265K | GPU: RX 9070 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2479 | Voorraad: 0

Model: Nova Pro - RX 9070 XT 16GB Prime | SKU: RNP-INTEL-R97XT | CPU: Intel Core Ultra 7 265K | GPU: RX 9070 XT 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2629 | Voorraad: 0

Model: Nova Pro - RTX 5070 Ti 16GB Prime | SKU: RNP-INTEL-N57T | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 Ti 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2899 | Voorraad: 0

Model: Nova Pro - RTX 5080 16GB Prime | SKU: RNP-INTEL-N58 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5080 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 3349 | Voorraad: 0

Model: Nova Pro White - RTX 5060 8GB Dual White | SKU: RNP-W-AMD-N56 | CPU: AMD Ryzen 5 9600X | GPU: RTX 5060 8GB Dual White | RAM: 32GB DDR5 Kingston Fury Beast RGB White | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2379 | Voorraad: 0

Model: Nova Pro White - RX 9060 XT 16GB Dual White | SKU: RNP-W-AMD-R96XT | CPU: AMD Ryzen 5 9600X | GPU: RX 9060 XT 16GB Dual White | RAM: 32GB DDR5 Kingston Fury Beast RGB White | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2529 | Voorraad: 0

Model: Nova Pro White - RTX 5060 Ti 16GB Dual White | SKU: RNP-W-AMD-N56T | CPU: AMD Ryzen 5 9600X | GPU: RTX 5060 Ti 16GB Dual White | RAM: 32GB DDR5 Kingston Fury Beast RGB White | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2679 | Voorraad: 0

Model: Nova Pro White - RTX 5070 12GB Prime White | SKU: RNP-W-AMD-N57 | CPU: AMD Ryzen 7 9700X | GPU: RTX 5070 12GB Prime White | RAM: 32GB DDR5 Kingston Fury Beast RGB White | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2849 | Voorraad: 0

Model: Nova Pro White - RX 9070 XT 16GB Prime White | SKU: RNP-W-AMD-R97XT | CPU: AMD Ryzen 7 9700X | GPU: RX 9070 XT 16GB Prime White | RAM: 32GB DDR5 Kingston Fury Beast RGB White | SSD: 1TB Kingston NV3 | Actieprijs: EUR 3029 | Voorraad: 0

Model: Nova - Arc B580 12GB | SKU: NOVA-AMD-D4-B58 | CPU: AMD Ryzen 5 5600 | GPU: Arc B580 12GB | RAM: 16GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1449 | Voorraad: 0

Model: Nova - RTX 5050 8GB Dual | SKU: NOVA-AMD-D4-N55 | CPU: AMD Ryzen 5 5600 | GPU: RTX 5050 8GB Dual | RAM: 16GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1479 | Voorraad: 0

Model: Nova - RTX 5050 8GB Dual | SKU: NOVA-AMD-N55 | CPU: AMD Ryzen 5 7500F | GPU: RTX 5050 8GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1579 | Voorraad: 1

Model: Nova - RTX 5060 8GB Dual | SKU: NOVA-AMD-N56 | CPU: AMD Ryzen 5 7500F | GPU: RTX 5060 8GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1649 | Voorraad: 1

Model: Nova - RX 9060 XT 16GB Dual | SKU: NOVA-AMD-R96XT | CPU: AMD Ryzen 5 7500F | GPU: RX 9060 XT 16GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1779 | Voorraad: 0

Model: Nova - RTX 5060 Ti 16GB Dual | SKU: NOVA-AMD-N56T | CPU: AMD Ryzen 5 7500F | GPU: RTX 5060 Ti 16GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1979 | Voorraad: 0

Model: Nova - RTX 5060 8GB Dual | SKU: NOVA-AMD-D4-N56 | CPU: AMD Ryzen 5 5600 | GPU: RTX 5060 8GB Dual | RAM: 16GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1579 | Voorraad: 3

Model: Nova - RTX 5060 Ti 8GB Dual | SKU: NOVA-AMD-D4-N56T8 | CPU: AMD Ryzen 7 5700X | GPU: RTX 5060 Ti 8GB Dual | RAM: 16GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1699 | Voorraad: 0

Model: Nova - RX 9060 XT 16GB Dual | SKU: NOVA-AMD-D4-R96XT | CPU: AMD Ryzen 7 5700X | GPU: RX 9060 XT 16GB Dual | RAM: 16GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1729 | Voorraad: 1

Model: Nova - RTX 5060 Ti 16GB Dual | SKU: NOVA-AMD-D4-N56T | CPU: AMD Ryzen 7 5700X | GPU: RTX 5060 Ti 16GB Dual | RAM: 16GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1899 | Voorraad: 2

Model: Nova - RTX 5070 12GB Dual | SKU: NOVA-AMD-D4-N57 | CPU: AMD Ryzen 7 5700X | GPU: RTX 5070 12GB Dual | RAM: 16GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1979 | Voorraad: 0

Model: Nova - RTX 5070 12GB Dual | SKU: NOVA-AMD-N57 | CPU: AMD Ryzen 7 7700 | GPU: RTX 5070 12GB Dual | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2129 | Voorraad: 0

Model: Nova - RX 9070 16GB Prime | SKU: NOVA-AMD-R97 | CPU: AMD Ryzen 7 7700 | GPU: RX 9070 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2199 | Voorraad: 1

Model: Nova - RX 9070 XT 16GB Prime | SKU: NOVA-AMD-R97XT | CPU: AMD Ryzen 7 7700 | GPU: RX 9070 XT 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2349 | Voorraad: 0

Model: Nova - RTX 5070 Ti 16GB Prime | SKU: NOVA-AMD-N57T | CPU: AMD Ryzen 7 7700 | GPU: RTX 5070 Ti 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 2629 | Voorraad: 1

Model: Nova - RTX 5080 16GB Prime | SKU: NOVA-AMD-N58 | CPU: AMD Ryzen 7 7700 | GPU: RTX 5080 16GB Prime | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 3079 | Voorraad: 0

Model: Andromeda Touch - RX 9070 XT 16GB TUF | SKU: RAT-AMD-R97XT | CPU: AMD Ryzen 7 9850X3D | GPU: RX 9070 XT 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4529 | Voorraad: 0

Model: Andromeda Touch - RX 9070 XT 16GB TUF | SKU: RAT-INTEL-R97XT | CPU: Intel Core Ultra 9 285K | GPU: RX 9070 XT 16GB TUF | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4749 | Voorraad: 0

Model: Andromeda Touch - RTX 5070 Ti 16GB Strix | SKU: RAT-AMD-N57T | CPU: AMD Ryzen 7 9850X3D | GPU: RTX 5070 Ti 16GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4879 | Voorraad: 0

Model: Andromeda Touch - RTX 5070 Ti 16GB Strix | SKU: RAT-INTEL-N57T | CPU: Intel Core Ultra 9 285K | GPU: RTX 5070 Ti 16GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 5079 | Voorraad: 0

Model: Andromeda Touch - RTX 5080 16GB Astral | SKU: RAT-AMD-N58 | CPU: AMD Ryzen 7 9850X3D | GPU: RTX 5080 16GB Astral | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 5429 | Voorraad: 1

Model: Andromeda Touch - RTX 5080 16GB Astral | SKU: RAT-INTEL-N58 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5080 16GB Astral | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 5629 | Voorraad: 0

Model: Andromeda Touch - RTX 5090 32GB Astral | SKU: RAT-AMD-N59 | CPU: AMD Ryzen 7 9850X3D | GPU: RTX 5090 32GB Astral | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 7379 | Voorraad: 0

Model: Andromeda Touch - RTX 5090 32GB Astral | SKU: RAT-INTEL-N59 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5090 32GB Astral | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 7579 | Voorraad: 0

Model: Andromeda II - RTX 5070 12GB Strix | SKU: RAII-INTEL-N57 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 12GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4029 | Voorraad: 0

Model: Andromeda II - RTX 5070 12GB Strix | SKU: RAII-AMD-N57 | CPU: AMD Ryzen 7 9850X3D | GPU: RTX 5070 12GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4129 | Voorraad: 0

Model: Andromeda II - RTX 5070 Ti 16GB Strix | SKU: RAII-INTEL-N57T | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 Ti 16GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4479 | Voorraad: 0

Model: Andromeda II - RTX 5070 Ti 16GB Strix | SKU: RAII-AMD-N57T | CPU: AMD Ryzen 7 9850X3D | GPU: RTX 5070 Ti 16GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4549 | Voorraad: 0

Model: Andromeda II - RTX 5080 16GB Astral | SKU: RAII-AMD-N58 | CPU: AMD Ryzen 7 9850X3D | GPU: RTX 5080 16GB Astral | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 5079 | Voorraad: 0

Model: Andromeda II - RTX 5080 16GB Astral | SKU: RAII-INTEL-N58 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5080 16GB Astral | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 5329 | Voorraad: 0

Model: Andromeda II - RTX 5090 32GB Astral | SKU: RAII-AMD-N59 | CPU: AMD Ryzen 7 9850X3D | GPU: RTX 5090 32GB Astral | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 7029 | Voorraad: 0

Model: Andromeda II - RTX 5090 32GB Astral | SKU: RAII-INTEL-N59 | CPU: Intel Core Ultra 9 285K | GPU: RTX 5090 32GB Astral | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 7279 | Voorraad: 0

Model: Strix Pro - RTX 5070 12GB Strix | SKU: STRIX-PRO-INTEL-N57 | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 12GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3299 | Voorraad: 0

Model: Strix Pro - RTX 5070 12GB Strix | SKU: STRIX-PRO-AMD-N57 | CPU: AMD Ryzen 7 9800X3D | GPU: RTX 5070 12GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3449 | Voorraad: 0

Model: Strix Pro - RTX 5070 Ti 16GB Strix | SKU: STRIX-PRO-INTEL-N57T | CPU: Intel Core Ultra 7 265K | GPU: RTX 5070 Ti 16GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3729 | Voorraad: 0

Model: Strix Pro - RTX 5070 Ti 16GB Strix | SKU: STRIX-PRO-AMD-N57T | CPU: AMD Ryzen 7 9800X3D | GPU: RTX 5070 Ti 16GB Strix | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Kingston NV3 | Actieprijs: EUR 3879 | Voorraad: 0

Model: Nighthawk - RX 9060 XT 16GB Prime | SKU: RNH-AMD-R96XT | CPU: AMD Ryzen 9 7900 | GPU: RX 9060 XT 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3029 | Voorraad: 0

Model: Nighthawk - RTX 5060 Ti 16GB Prime | SKU: RNH-AMD-N56T | CPU: AMD Ryzen 9 7900 | GPU: RTX 5060 Ti 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3179 | Voorraad: 0

Model: Nighthawk - RTX 5070 12GB Prime | SKU: RNH-AMD-N57 | CPU: AMD Ryzen 9 7900 | GPU: RTX 5070 12GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3279 | Voorraad: 0

Model: Nighthawk - RX 9070 16GB Prime | SKU: RNH-AMD-R97 | CPU: AMD Ryzen 9 7900 | GPU: RX 9070 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3299 | Voorraad: 0

Model: Nighthawk - RTX 5060 Ti 16GB Prime | SKU: RNH-INTEL-N56T | CPU: Intel Core Ultra 7 265K | GPU: RTX 5060 Ti 16GB Prime | RAM: 48GB DDR5 G.Skill Trident Z5 Neo RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3399 | Voorraad: 0

Model: Nighthawk - RX 9070 XT 16GB Prime | SKU: RNH-AMD-R97XT | CPU: AMD Ryzen 9 9900X | GPU: RX 9070 XT 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3549 | Voorraad: 0

Model: Nighthawk - RTX 5070 Ti 16GB Prime | SKU: RNH-AMD-N57T | CPU: AMD Ryzen 9 9900X | GPU: RTX 5070 Ti 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 3799 | Voorraad: 0

Model: Nighthawk - RTX 5080 16GB Prime | SKU: RNH-AMD-N58 | CPU: AMD Ryzen 9 9900X | GPU: RTX 5080 16GB Prime | RAM: 32GB DDR5 Kingston Fury Beast RGB | SSD: 2TB Samsung 990 EVO Plus | Actieprijs: EUR 4249 | Voorraad: 0

Model: ActiePC - RTX 5070 Ti 16GB Inno3D X3 | SKU: ACTIE-N57T | CPU: AMD Ryzen 7 7800X3D | GPU: RTX 5070 Ti 16GB Inno3D X3 | RAM: 32GB DDR5 Viper Venom | SSD: 1TB Patriot Viper VP4300 Lite | Actieprijs: EUR 2699 | Voorraad: 0

Model: Nova - RTX 3050 6GB Dual | SKU: NOVA-AMD-D4-N35 | CPU: AMD Ryzen 5 5600 | GPU: RTX 3050 6GB Dual | RAM: 16GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1379 | Voorraad: 0

Model: Nova - Geen | SKU: NOVA-AMD-D4 | CPU: AMD Ryzen 5 5600G | GPU: Geen | RAM: 16GB DDR4 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1129 | Voorraad: 0

Model: Nova - Geen | SKU: NOVA-AMD | CPU: AMD Ryzen 5 8600G | GPU: Geen | RAM: 16GB DDR5 Kingston Fury Beast RGB | SSD: 1TB Kingston NV3 | Actieprijs: EUR 1199 | Voorraad: 0

Model: Oud/nieuw - CPU | SKU: SKU | CPU: Lijn | GPU: CPU | RAM: Moederbord | SSD: RAM | Actieprijs: EUR Uitgaand | Voorraad: Marge

# ACCESSOIRES & PERIPHERALS
Model: Andromeda II AMD N57T | SKU: RAII-AMD-N57T | Prijs: EUR 4.549,00

Model: Andromeda II AMD N58 | SKU: RAII-AMD-N58 | Prijs: EUR 4.999,00

Model: Andromeda II AMD N59 | SKU: RAII-AMD-N59 | Prijs: EUR 6.999,00

Model: Andromeda II Intel N57T | SKU: RAII-INTEL-N57T | Prijs: EUR 4.479,00

Model: Andromeda II Intel N58 | SKU: RAII-INTEL-N58 | Prijs: EUR 5.329,00

Model: Andromeda II Intel N59 | SKU: RAII-INTEL-N59 | Prijs: EUR 7.149,00

Model: Andromeda Touch AMD N57T | SKU: RAT-AMD-N57T | Prijs: EUR 4.879,00

Model: Andromeda Touch AMD N58 | SKU: RAT-AMD-N58 | Prijs: EUR 5.429,00

Model: Andromeda Touch AMD N59 | SKU: RAT-AMD-N59 | Prijs: EUR 7.279,00

Model: Andromeda Touch Intel N57T | SKU: RAT-INTEL-N57T | Prijs: EUR 4.999,00

Model: Andromeda Touch Intel N58 | SKU: RAT-INTEL-N58 | Prijs: EUR 5.629,00

Model: Andromeda Touch Intel N59 | SKU: RAT-INTEL-N59 | Prijs: EUR 7.479,00

Model: ASUS ROG Delta II | SKU: 90YH03W0-BHUA00 | Prijs: EUR 229,99

Model: ASUS ROG Delta | SKU: 90YH00Z1-B2UA00 | Prijs: EUR 179,99

Model: ASUS ROG Falchion ACE HFX | SKU: 90MP03VE-BKUA20 | Prijs: EUR 229,99

Model: ASUS ROG Hone ACE Aim Lab | SKU: 90MP0380-BPUA00 | Prijs: EUR 53,99

Model: ASUS ROG Pelta | SKU: 90YH0410-BHUA00 | Prijs: EUR 149,99

Model: ASUS ROG Raikiri Pro | SKU: 90GC00W0-BGP000 | Prijs: EUR 167,99

Model: ASUS ROG Raikiri | SKU: 90GC00X0-BGP000 | Prijs: EUR 117,99

Model: ASUS ROG Sheath BLK LTD | SKU: 90MP00K3-B0UA00 | Prijs: EUR 53,99

Model: ASUS ROG Sheath | SKU: 90MP00K1-B0UA00 | Prijs: EUR 61,99

Model: ASUS ROG Strix Impact III Wireless | SKU: 90MP03D0-BMUA00 | Prijs: EUR 69,99

Model: ASUS ROG Strix OLED XG27ACDNG | SKU: 90LM0AN0-B01970 | Prijs: EUR 799,99

Model: ASUS ROG Strix OLED XG27AQDMG | SKU: 90LM0AH0-B01A70 | Prijs: EUR 549,99

Model: ASUS ROG Strix OLED XG27UCDMG | SKU: 90LM0B20-B01971 | Prijs: EUR 899,99

Model: ASUS ROG Strix Scope II 96 Wireless | SKU: 90MP037A-BKUA01 | Prijs: EUR 199,99

Model: ASUS ROG Strix XG27UCS | SKU: 90LM09S0-B01170 | Prijs: EUR 399,99

Model: ASUS ROG Strix XG27WCS | SKU: 90LM09P1-B01370 | Prijs: EUR 327,99

Model: ASUS ROG Strix OLED XG32UCWMG | SKU: 90LM0BW0-B01371 | Prijs: EUR 1.199,99

Model: ASUS ROG Strix XG32WCS | SKU: 90LM0AC0-B01970 | Prijs: EUR 329,99

Model: ASUS TUF Gaming H1 Gen II | SKU: 90YH044B-BHUA00 | Prijs: EUR 63,99

Model: ASUS TUF Gaming M3 Gen II | SKU: 90MP0320-BMUA00 | Prijs: EUR 37,99

Model: ASUS TUF Gaming VG259Q5A | SKU: 90LM0BL1-B01O71 | Prijs: EUR 149,99

Model: ASUS TUF Gaming VG279Q5A | SKU: 90LM0C30-B01171 | Prijs: EUR 179,99

Model: ASUS TUF Gaming VG279QL3A | SKU: 90LM09H0-B01170 | Prijs: EUR 199,99

Model: ASUS TUF Gaming VG27AQ5A | SKU: 90LM0BN0-B01371 | Prijs: EUR 249,99

Model: ASUS TUF Gaming VG27AQML5A | SKU: 90LM0BG0-B02971 | Prijs: EUR 389,99

Model: ASUS TUF Gaming VG32AQA1A | SKU: 90LM07L0-B02370 | Prijs: EUR 319,99

Model: ASUS TUF Gaming VG34WQML5A | SKU: 90LM0BP1-B01E71 | Prijs: EUR 449,99

Model: BenQ ZA12-B | SKU: 9H.N2VBB.A2E | Prijs: EUR 25,99

Model: BenQ ZOWIE ZA11-B | SKU: 9H.N2TBB.A2E-1 | Prijs: EUR 29,90

Model: Endorfy AXIS Streaming Microfoon | SKU: EY1B006 | Prijs: EUR 103,99

Model: Endorfy Gem Plus Onyx White | SKU: EY6A011 | Prijs: EUR 33,99

Model: Endorfy Gem Plus Wireless | SKU: EY6A013 | Prijs: EUR 79,99

Model: Endorfy Gem | SKU: EY6A006 | Prijs: EUR 27,99

Model: Endorfy Solum Streaming T | SKU: EY1B003 | Prijs: EUR 49,99

Model: Endorfy Solum Voice S | SKU: EY1B013 | Prijs: EUR 55,99

Model: Endorfy Thock 75% RGB Wireless Black switch | SKU: EY5A074 | Prijs: EUR 77,99

Model: Genesis Krypton 290 RGB wit | SKU: NMG-1785 | Prijs: EUR 15,99

Model: Genesis Krypton 750 RGB Wit | SKU: NMG-1842 | Prijs: EUR 29,99

Model: Genesis Krypton 750 RGB | SKU: NMG-1841 | Prijs: EUR 29,99

Model: Logitech G PRO X 2 Lightspeed | SKU: 981-001263 | Prijs: EUR 219,99

Model: Logitech G Pro X Superlight 2 | SKU: 910-006631 | Prijs: EUR 149,99

Model: Logitech G PRO X | SKU: 981-000818 | Prijs: EUR 99,99

Model: Logitech G213 Prodigy RGB | SKU: 920-008093 | Prijs: EUR 59,99

Model: Logitech G305 | SKU: 910-005283 | Prijs: EUR 49,99

Model: Logitech G515 Lightspeed TKL (GL Tactile switch) | SKU: 920-012538 | Prijs: EUR 139,99

Model: Nighthawk AMD N56T16 | SKU: RNH-AMD-N56T | Prijs: EUR 3.179,00

Model: Nighthawk AMD N57T | SKU: RNH-AMD-N57T | Prijs: EUR 3.799,00

Model: Nighthawk AMD N58 | SKU: RNH-AMD-N58 | Prijs: EUR 4.249,00

Model: Nighthawk AMD R96XT | SKU: RNH-AMD-R96XT | Prijs: EUR 2.999,00

Model: Nighthawk AMD R97 | SKU: RNH-AMD-R97 | Prijs: EUR 3.299,00

Model: Nighthawk AMD R97XT | SKU: RNH-AMD-R97XT | Prijs: EUR 3.549,00

Model: Nova AMD N55 | SKU: NOVA-AMD-D4-N55 | Prijs: EUR 1.479,00

Model: Nova AMD N56 | SKU: NOVA-AMD-D4-N56 | Prijs: EUR 1.549,00

Model: Nova AMD N56T16 | SKU: NOVA-AMD-D4-N56T | Prijs: EUR 1.899,00

Model: Nova AMD N56T8 | SKU: NOVA-AMD-D4-N56T8 | Prijs: EUR 1.699,00

Model: Nova AMD N57 | SKU: NOVA-AMD-D4-N57 | Prijs: EUR 1.979,00

Model: Nova AMD R96XT | SKU: NOVA-AMD-D4-R96XT | Prijs: EUR 1.729,00

Model: Nova Pro AMD N55 | SKU: NOVA-AMD-N55 | Prijs: EUR 1.579,00

Model: Nova Pro AMD N56 | SKU: NOVA-AMD-N56 | Prijs: EUR 1.649,00

Model: Nova Pro AMD N56T16 | SKU: NOVA-AMD-N56T | Prijs: EUR 1.949,00

Model: Nova Pro AMD N56T8 | SKU: NOVA-AMD-N56T8 | Prijs: EUR 1.779,00

Model: Nova Pro AMD N57 | SKU: NOVA-AMD-N57 | Prijs: EUR 2.129,00

Model: Nova Pro AMD N57T | SKU: NOVA-AMD-N57T | Prijs: EUR 2.629,00

Model: Nova Pro AMD N58 | SKU: NOVA-AMD-N58 | Prijs: EUR 3.079,00

Model: Nova Pro AMD R96XT | SKU: NOVA-AMD-R96XT | Prijs: EUR 1.779,00

Model: Nova Pro AMD R97 | SKU: NOVA-AMD-R97 | Prijs: EUR 2.199,00

Model: Nova Pro AMD R97XT | SKU: NOVA-AMD-R97XT | Prijs: EUR 2.349,00

Model: Nova Pro White AMD N56 | SKU: RNP-W-AMD-N56 | Prijs: EUR 2.379,00

Model: Nova Pro White AMD N56T16 | SKU: RNP-W-AMD-N56T | Prijs: EUR 2.679,00

Model: Nova Pro White AMD R96XT | SKU: RNP-W-AMD-R96XT | Prijs: EUR 2.529,00

Model: Outlet PC MSI Cubi | SKU: Outlet PC MSI Cubi | Prijs: EUR 99,00

Model: Prism AMD N56 | SKU: PRISM-AMD-N56 | Prijs: EUR 2.279,00

Model: Prism AMD N56T16 | SKU: PRISM-AMD-N56T | Prijs: EUR 2.579,00

Model: Prism AMD N56T8 | SKU: PRISM-AMD-N56T8 | Prijs: EUR 2.379,00

Model: Prism AMD N57 | SKU: PRISM-AMD-N57 | Prijs: EUR 2.679,00

Model: Prism AMD N57T | SKU: PRISM-AMD-N57T | Prijs: EUR 3.249,00

Model: Prism AMD N58 | SKU: PRISM-AMD-N58 | Prijs: EUR 3.699,00

Model: Prism AMD N59 | SKU: PRISM-AMD-N59 | Prijs: EUR 5.579,00

Model: Prism AMD R96XT | SKU: PRISM-AMD-R96XT | Prijs: EUR 2.399,00

Model: Prism AMD R97XT | SKU: PRISM-AMD-R97XT | Prijs: EUR 2.979,00

Model: Prism Intel N56 | SKU: PRISM-INTEL-N56 | Prijs: EUR 2.199,00

Model: Prism Intel N56T16 | SKU: PRISM-INTEL-N56T | Prijs: EUR 2.499,00

Model: Prism Intel N56T8 | SKU: PRISM-INTEL-N56T8 | Prijs: EUR 2.329,00

Model: Prism Intel N57 | SKU: PRISM-INTEL-N57 | Prijs: EUR 2.599,00

Model: Prism Intel N57T | SKU: PRISM-INTEL-N57T | Prijs: EUR 3.279,00

Model: Prism Intel N58 | SKU: PRISM-INTEL-N58 | Prijs: EUR 3.729,00

Model: Prism Intel N59 | SKU: PRISM-INTEL-N59 | Prijs: EUR 5.799,00

Model: Prism White AMD N57 | SKU: PRISM-WH-AMD-N57 | Prijs: EUR 2.829,00

Model: Prism White AMD R97XT | SKU: PRISM-WH-AMD-R97XT | Prijs: EUR 3.129,00

Model: Redux Abo Basic A75 R96XT | SKU: ABO-BASIC | Prijs: EUR 1.649,00

Model: Redux Abo Premium A98X3D N57T | SKU: ABO-PREMIUM | Prijs: EUR 2.679,00

Model: Redux Basic Abonnement - 24 maanden | SKU: B-24 | Prijs: EUR 74,95

Model: Redux Basic Abonnement - Flex | SKU: B-F | Prijs: EUR 114,95

Model: Redux E-Sports Abonnement - Flex | SKU: E-F | Prijs: EUR 149,95

Model: Redux Gaming XXL muismat | SKU: RG-M9 | Prijs: EUR 11,99

Model: Redux Gaming XXL RGB muismat | SKU: RG-M9-RGB | Prijs: EUR 17,99

Model: Redux Premium Abonnement - 24 maanden | SKU: P-24 | Prijs: EUR 119,95

Model: Redux Premium Abonnement - Flex | SKU: P-F | Prijs: EUR 184,95

Model: Redux Hyperion AMD N59 - Powered by ASUS | SKU: ROGH-AMD-N59 | Prijs: EUR 8.199,00

Model: Redux Hyperion Intel N59 - Powered by ASUS | SKU: ROGH-INTEL-N59 | Prijs: EUR 8.199,00

Model: Redux Liquid Ultimate AMD N59 - Powered by ASUS | SKU: ROGU-AMD-N59 | Prijs: EUR 8.999,00

Model: Redux Liquid Ultimate Intel N59 - Powered by ASUS | SKU: ROGU-INTEL-N59 | Prijs: EUR 8.999,00

Model: Redux Hatsune Miku AMD N58 - Powered by ASUS | SKU: HATSUNE-AMD-N58 | Prijs: EUR 5.699,00

Model: Redux Gamer Pro AMD N57 - Powered by ASUS | SKU: STRIX-PRO-AMD-N57 | Prijs: EUR 3.449,00

Model: Redux Gamer Pro AMD N57T - Powered by ASUS | SKU: STRIX-PRO-AMD-N57T | Prijs: EUR 3.879,00

Model: Redux Gamer Pro Intel N57 - Powered by ASUS | SKU: STRIX-PRO-INTEL-N57 | Prijs: EUR 3.299,00

Model: Redux Gamer Pro Intel N57T - Powered by ASUS | SKU: STRIX-PRO-INTEL-N57T | Prijs: EUR 3.729,00

Model: Redux Gamer Ultimate AMD N57T - Powered by ASUS | SKU: RTU-AMD-N57T | Prijs: EUR 4.479,00

Model: Redux Gamer Ultimate AMD N58 - Powered by ASUS | SKU: RTU-AMD-N58 | Prijs: EUR 4.979,00

Model: Redux Gamer Ultimate AMD N59 - Powered by ASUS | SKU: RTU-AMD-N59 | Prijs: EUR 6.779,00

Model: Redux Ultimate WS AMD N59 - Powered by ASUS | SKU: RUWS-AMD-N59 | Prijs: EUR 7.229,00

Model: Redux Ultimate WS Intel N57T - Powered by ASUS | SKU: RUWS-INTEL-N57T | Prijs: EUR 4.649,00

Model: Redux Ultimate WS Intel N58 - Powered by ASUS | SKU: RUWS-INTEL-N58 | Prijs: EUR 5.579,00

Model: Redux Ultimate WS Intel N59 - Powered by ASUS | SKU: RUWS-INTEL-N59 | Prijs: EUR 7.329,00

Model: Redux X NoaNoella AMD N57T - Powered by ASUS | SKU: RDX-NN-AMD-N57T | Prijs: EUR 3.899,00

Model: Supernova AMD N56 | SKU: RSN-AMD-N56 | Prijs: EUR 2.529,00

Model: Supernova AMD N56T16 | SKU: RSN-AMD-N56T | Prijs: EUR 2.829,00

Model: Supernova AMD N56T8 | SKU: RSN-AMD-N56T8 | Prijs: EUR 2.679,00

Model: Supernova AMD N57 | SKU: RSN-AMD-N57 | Prijs: EUR 2.999,00

Model: Supernova AMD N57T | SKU: RSN-AMD-N57T | Prijs: EUR 3.479,00

Model: Supernova AMD N58 | SKU: RSN-AMD-N58 | Prijs: EUR 3.979,00

Model: Supernova AMD N59 | SKU: RSN-AMD-N59 | Prijs: EUR 5.799,00

Model: Supernova AMD R96XT | SKU: RSN-AMD-R96XT | Prijs: EUR 2.679,00

Model: Supernova AMD R97 | SKU: RSN-AMD-R97 | Prijs: EUR 2.999,00

Model: Supernova AMD R97XT | SKU: RSN-AMD-R97XT | Prijs: EUR 3.229,00

Model: Supernova Intel N56T16 | SKU: RSN-INTEL-N56T | Prijs: EUR 2.749,00

Model: Supernova Intel N57T | SKU: RSN-INTEL-N57T | Prijs: EUR 3.329,00

Model: Supernova Intel N58 | SKU: RSN-INTEL-N58 | Prijs: EUR 3.829,00

Model: Supernova Intel N59 | SKU: RSN-INTEL-N59 | Prijs: EUR 5.629,00

Model: White Shark Sagramore | SKU: SAGRAMORE | Prijs: EUR 21,99"""



ACCESSOIRES_DATA = """Product: Andromeda II AMD N57T | SKU: RAII-AMD-N57T | Prijs: EUR 4.549,00
Product: Andromeda II AMD N58 | SKU: RAII-AMD-N58 | Prijs: EUR 4.999,00
Product: Andromeda II AMD N59 | SKU: RAII-AMD-N59 | Prijs: EUR 6.999,00
Product: Andromeda II Intel N57T | SKU: RAII-INTEL-N57T | Prijs: EUR 4.479,00
Product: Andromeda II Intel N58 | SKU: RAII-INTEL-N58 | Prijs: EUR 5.329,00
Product: Andromeda II Intel N59 | SKU: RAII-INTEL-N59 | Prijs: EUR 7.149,00
Product: Andromeda Touch AMD N57T | SKU: RAT-AMD-N57T | Prijs: EUR 4.879,00
Product: Andromeda Touch AMD N58 | SKU: RAT-AMD-N58 | Prijs: EUR 5.429,00
Product: Andromeda Touch AMD N59 | SKU: RAT-AMD-N59 | Prijs: EUR 7.279,00
Product: Andromeda Touch Intel N57T | SKU: RAT-INTEL-N57T | Prijs: EUR 4.999,00
Product: Andromeda Touch Intel N58 | SKU: RAT-INTEL-N58 | Prijs: EUR 5.629,00
Product: Andromeda Touch Intel N59 | SKU: RAT-INTEL-N59 | Prijs: EUR 7.479,00
Product: ASUS ROG Delta II | SKU: 90YH03W0-BHUA00 | Prijs: EUR 229,99
Product: ASUS ROG Delta | SKU: 90YH00Z1-B2UA00 | Prijs: EUR 179,99
Product: ASUS ROG Falchion ACE HFX | SKU: 90MP03VE-BKUA20 | Prijs: EUR 229,99
Product: ASUS ROG Hone ACE Aim Lab | SKU: 90MP0380-BPUA00 | Prijs: EUR 53,99
Product: ASUS ROG Pelta | SKU: 90YH0410-BHUA00 | Prijs: EUR 149,99
Product: ASUS ROG Raikiri Pro | SKU: 90GC00W0-BGP000 | Prijs: EUR 167,99
Product: ASUS ROG Raikiri | SKU: 90GC00X0-BGP000 | Prijs: EUR 117,99
Product: ASUS ROG Sheath BLK LTD | SKU: 90MP00K3-B0UA00 | Prijs: EUR 53,99
Product: ASUS ROG Sheath | SKU: 90MP00K1-B0UA00 | Prijs: EUR 61,99
Product: ASUS ROG Strix Impact III Wireless | SKU: 90MP03D0-BMUA00 | Prijs: EUR 69,99
Product: ASUS ROG Strix OLED XG27ACDNG | SKU: 90LM0AN0-B01970 | Prijs: EUR 799,99
Product: ASUS ROG Strix OLED XG27AQDMG | SKU: 90LM0AH0-B01A70 | Prijs: EUR 549,99
Product: ASUS ROG Strix OLED XG27UCDMG | SKU: 90LM0B20-B01971 | Prijs: EUR 899,99
Product: ASUS ROG Strix Scope II 96 Wireless | SKU: 90MP037A-BKUA01 | Prijs: EUR 199,99
Product: ASUS ROG Strix XG27UCS | SKU: 90LM09S0-B01170 | Prijs: EUR 399,99
Product: ASUS ROG Strix XG27WCS | SKU: 90LM09P1-B01370 | Prijs: EUR 327,99
Product: ASUS ROG Strix OLED XG32UCWMG | SKU: 90LM0BW0-B01371 | Prijs: EUR 1.199,99
Product: ASUS ROG Strix XG32WCS | SKU: 90LM0AC0-B01970 | Prijs: EUR 329,99
Product: ASUS TUF Gaming H1 Gen II | SKU: 90YH044B-BHUA00 | Prijs: EUR 63,99
Product: ASUS TUF Gaming M3 Gen II | SKU: 90MP0320-BMUA00 | Prijs: EUR 37,99
Product: ASUS TUF Gaming VG259Q5A | SKU: 90LM0BL1-B01O71 | Prijs: EUR 149,99
Product: ASUS TUF Gaming VG279Q5A | SKU: 90LM0C30-B01171 | Prijs: EUR 179,99
Product: ASUS TUF Gaming VG279QL3A | SKU: 90LM09H0-B01170 | Prijs: EUR 199,99
Product: ASUS TUF Gaming VG27AQ5A | SKU: 90LM0BN0-B01371 | Prijs: EUR 249,99
Product: ASUS TUF Gaming VG27AQML5A | SKU: 90LM0BG0-B02971 | Prijs: EUR 389,99
Product: ASUS TUF Gaming VG32AQA1A | SKU: 90LM07L0-B02370 | Prijs: EUR 319,99
Product: ASUS TUF Gaming VG34WQML5A | SKU: 90LM0BP1-B01E71 | Prijs: EUR 449,99
Product: BenQ ZA12-B | SKU: 9H.N2VBB.A2E | Prijs: EUR 25,99
Product: BenQ ZOWIE ZA11-B | SKU: 9H.N2TBB.A2E-1 | Prijs: EUR 29,90
Product: Endorfy AXIS Streaming Microfoon | SKU: EY1B006 | Prijs: EUR 103,99
Product: Endorfy Gem Plus Onyx White | SKU: EY6A011 | Prijs: EUR 33,99
Product: Endorfy Gem Plus Wireless | SKU: EY6A013 | Prijs: EUR 79,99
Product: Endorfy Gem | SKU: EY6A006 | Prijs: EUR 27,99
Product: Endorfy Solum Streaming T | SKU: EY1B003 | Prijs: EUR 49,99
Product: Endorfy Solum Voice S | SKU: EY1B013 | Prijs: EUR 55,99
Product: Endorfy Thock 75% RGB Wireless Black switch | SKU: EY5A074 | Prijs: EUR 77,99
Product: Genesis Krypton 290 RGB wit | SKU: NMG-1785 | Prijs: EUR 15,99
Product: Genesis Krypton 750 RGB Wit | SKU: NMG-1842 | Prijs: EUR 29,99
Product: Genesis Krypton 750 RGB | SKU: NMG-1841 | Prijs: EUR 29,99
Product: Logitech G PRO X 2 Lightspeed | SKU: 981-001263 | Prijs: EUR 219,99
Product: Logitech G Pro X Superlight 2 | SKU: 910-006631 | Prijs: EUR 149,99
Product: Logitech G PRO X | SKU: 981-000818 | Prijs: EUR 99,99
Product: Logitech G213 Prodigy RGB | SKU: 920-008093 | Prijs: EUR 59,99
Product: Logitech G305 | SKU: 910-005283 | Prijs: EUR 49,99
Product: Logitech G515 Lightspeed TKL (GL Tactile switch) | SKU: 920-012538 | Prijs: EUR 139,99
Product: Nighthawk AMD N56T16 | SKU: RNH-AMD-N56T | Prijs: EUR 3.179,00
Product: Nighthawk AMD N57T | SKU: RNH-AMD-N57T | Prijs: EUR 3.799,00
Product: Nighthawk AMD N58 | SKU: RNH-AMD-N58 | Prijs: EUR 4.249,00
Product: Nighthawk AMD R96XT | SKU: RNH-AMD-R96XT | Prijs: EUR 2.999,00
Product: Nighthawk AMD R97 | SKU: RNH-AMD-R97 | Prijs: EUR 3.299,00
Product: Nighthawk AMD R97XT | SKU: RNH-AMD-R97XT | Prijs: EUR 3.549,00
Product: Nova AMD N55 | SKU: NOVA-AMD-D4-N55 | Prijs: EUR 1.479,00
Product: Nova AMD N56 | SKU: NOVA-AMD-D4-N56 | Prijs: EUR 1.549,00
Product: Nova AMD N56T16 | SKU: NOVA-AMD-D4-N56T | Prijs: EUR 1.899,00
Product: Nova AMD N56T8 | SKU: NOVA-AMD-D4-N56T8 | Prijs: EUR 1.699,00
Product: Nova AMD N57 | SKU: NOVA-AMD-D4-N57 | Prijs: EUR 1.979,00
Product: Nova AMD R96XT | SKU: NOVA-AMD-D4-R96XT | Prijs: EUR 1.729,00
Product: Nova Pro AMD N55 | SKU: NOVA-AMD-N55 | Prijs: EUR 1.579,00
Product: Nova Pro AMD N56 | SKU: NOVA-AMD-N56 | Prijs: EUR 1.649,00
Product: Nova Pro AMD N56T16 | SKU: NOVA-AMD-N56T | Prijs: EUR 1.949,00
Product: Nova Pro AMD N56T8 | SKU: NOVA-AMD-N56T8 | Prijs: EUR 1.779,00
Product: Nova Pro AMD N57 | SKU: NOVA-AMD-N57 | Prijs: EUR 2.129,00
Product: Nova Pro AMD N57T | SKU: NOVA-AMD-N57T | Prijs: EUR 2.629,00
Product: Nova Pro AMD N58 | SKU: NOVA-AMD-N58 | Prijs: EUR 3.079,00
Product: Nova Pro AMD R96XT | SKU: NOVA-AMD-R96XT | Prijs: EUR 1.779,00
Product: Nova Pro AMD R97 | SKU: NOVA-AMD-R97 | Prijs: EUR 2.199,00
Product: Nova Pro AMD R97XT | SKU: NOVA-AMD-R97XT | Prijs: EUR 2.349,00
Product: Nova Pro White AMD N56 | SKU: RNP-W-AMD-N56 | Prijs: EUR 2.379,00
Product: Nova Pro White AMD N56T16 | SKU: RNP-W-AMD-N56T | Prijs: EUR 2.679,00
Product: Nova Pro White AMD R96XT | SKU: RNP-W-AMD-R96XT | Prijs: EUR 2.529,00
Product: Outlet PC MSI Cubi | SKU: Outlet PC MSI Cubi | Prijs: EUR 99,00
Product: Prism AMD N56 | SKU: PRISM-AMD-N56 | Prijs: EUR 2.279,00
Product: Prism AMD N56T16 | SKU: PRISM-AMD-N56T | Prijs: EUR 2.579,00
Product: Prism AMD N56T8 | SKU: PRISM-AMD-N56T8 | Prijs: EUR 2.379,00
Product: Prism AMD N57 | SKU: PRISM-AMD-N57 | Prijs: EUR 2.679,00
Product: Prism AMD N57T | SKU: PRISM-AMD-N57T | Prijs: EUR 3.249,00
Product: Prism AMD N58 | SKU: PRISM-AMD-N58 | Prijs: EUR 3.699,00
Product: Prism AMD N59 | SKU: PRISM-AMD-N59 | Prijs: EUR 5.579,00
Product: Prism AMD R96XT | SKU: PRISM-AMD-R96XT | Prijs: EUR 2.399,00
Product: Prism AMD R97XT | SKU: PRISM-AMD-R97XT | Prijs: EUR 2.979,00
Product: Prism Intel N56 | SKU: PRISM-INTEL-N56 | Prijs: EUR 2.199,00
Product: Prism Intel N56T16 | SKU: PRISM-INTEL-N56T | Prijs: EUR 2.499,00
Product: Prism Intel N56T8 | SKU: PRISM-INTEL-N56T8 | Prijs: EUR 2.329,00
Product: Prism Intel N57 | SKU: PRISM-INTEL-N57 | Prijs: EUR 2.599,00
Product: Prism Intel N57T | SKU: PRISM-INTEL-N57T | Prijs: EUR 3.279,00
Product: Prism Intel N58 | SKU: PRISM-INTEL-N58 | Prijs: EUR 3.729,00
Product: Prism Intel N59 | SKU: PRISM-INTEL-N59 | Prijs: EUR 5.799,00
Product: Prism White AMD N57 | SKU: PRISM-WH-AMD-N57 | Prijs: EUR 2.829,00
Product: Prism White AMD R97XT | SKU: PRISM-WH-AMD-R97XT | Prijs: EUR 3.129,00
Product: Redux Abo Basic A75 R96XT | SKU: ABO-BASIC | Prijs: EUR 1.649,00
Product: Redux Abo Premium A98X3D N57T | SKU: ABO-PREMIUM | Prijs: EUR 2.679,00
Product: Redux Basic Abonnement - 24 maanden | SKU: B-24 | Prijs: EUR 74,95
Product: Redux Basic Abonnement - Flex | SKU: B-F | Prijs: EUR 114,95
Product: Redux E-Sports Abonnement - Flex | SKU: E-F | Prijs: EUR 149,95
Product: Redux Gaming XXL muismat | SKU: RG-M9 | Prijs: EUR 11,99
Product: Redux Gaming XXL RGB muismat | SKU: RG-M9-RGB | Prijs: EUR 17,99
Product: Redux Premium Abonnement - 24 maanden | SKU: P-24 | Prijs: EUR 119,95
Product: Redux Premium Abonnement - Flex | SKU: P-F | Prijs: EUR 184,95
Product: Redux Hyperion AMD N59 - Powered by ASUS | SKU: ROGH-AMD-N59 | Prijs: EUR 8.199,00
Product: Redux Hyperion Intel N59 - Powered by ASUS | SKU: ROGH-INTEL-N59 | Prijs: EUR 8.199,00
Product: Redux Liquid Ultimate AMD N59 - Powered by ASUS | SKU: ROGU-AMD-N59 | Prijs: EUR 8.999,00
Product: Redux Liquid Ultimate Intel N59 - Powered by ASUS | SKU: ROGU-INTEL-N59 | Prijs: EUR 8.999,00
Product: Redux Hatsune Miku AMD N58 - Powered by ASUS | SKU: HATSUNE-AMD-N58 | Prijs: EUR 5.699,00
Product: Redux Gamer Pro AMD N57 - Powered by ASUS | SKU: STRIX-PRO-AMD-N57 | Prijs: EUR 3.449,00
Product: Redux Gamer Pro AMD N57T - Powered by ASUS | SKU: STRIX-PRO-AMD-N57T | Prijs: EUR 3.879,00
Product: Redux Gamer Pro Intel N57 - Powered by ASUS | SKU: STRIX-PRO-INTEL-N57 | Prijs: EUR 3.299,00
Product: Redux Gamer Pro Intel N57T - Powered by ASUS | SKU: STRIX-PRO-INTEL-N57T | Prijs: EUR 3.729,00
Product: Redux Gamer Ultimate AMD N57T - Powered by ASUS | SKU: RTU-AMD-N57T | Prijs: EUR 4.479,00
Product: Redux Gamer Ultimate AMD N58 - Powered by ASUS | SKU: RTU-AMD-N58 | Prijs: EUR 4.979,00
Product: Redux Gamer Ultimate AMD N59 - Powered by ASUS | SKU: RTU-AMD-N59 | Prijs: EUR 6.779,00
Product: Redux Ultimate WS AMD N59 - Powered by ASUS | SKU: RUWS-AMD-N59 | Prijs: EUR 7.229,00
Product: Redux Ultimate WS Intel N57T - Powered by ASUS | SKU: RUWS-INTEL-N57T | Prijs: EUR 4.649,00
Product: Redux Ultimate WS Intel N58 - Powered by ASUS | SKU: RUWS-INTEL-N58 | Prijs: EUR 5.579,00
Product: Redux Ultimate WS Intel N59 - Powered by ASUS | SKU: RUWS-INTEL-N59 | Prijs: EUR 7.329,00
Product: Redux X NoaNoella AMD N57T - Powered by ASUS | SKU: RDX-NN-AMD-N57T | Prijs: EUR 3.899,00
Product: Supernova AMD N56 | SKU: RSN-AMD-N56 | Prijs: EUR 2.529,00
Product: Supernova AMD N56T16 | SKU: RSN-AMD-N56T | Prijs: EUR 2.829,00
Product: Supernova AMD N56T8 | SKU: RSN-AMD-N56T8 | Prijs: EUR 2.679,00
Product: Supernova AMD N57 | SKU: RSN-AMD-N57 | Prijs: EUR 2.999,00
Product: Supernova AMD N57T | SKU: RSN-AMD-N57T | Prijs: EUR 3.479,00
Product: Supernova AMD N58 | SKU: RSN-AMD-N58 | Prijs: EUR 3.979,00
Product: Supernova AMD N59 | SKU: RSN-AMD-N59 | Prijs: EUR 5.799,00
Product: Supernova AMD R96XT | SKU: RSN-AMD-R96XT | Prijs: EUR 2.679,00
Product: Supernova AMD R97 | SKU: RSN-AMD-R97 | Prijs: EUR 2.999,00
Product: Supernova AMD R97XT | SKU: RSN-AMD-R97XT | Prijs: EUR 3.229,00
Product: Supernova Intel N56T16 | SKU: RSN-INTEL-N56T | Prijs: EUR 2.749,00
Product: Supernova Intel N57T | SKU: RSN-INTEL-N57T | Prijs: EUR 3.329,00
Product: Supernova Intel N58 | SKU: RSN-INTEL-N58 | Prijs: EUR 3.829,00
Product: Supernova Intel N59 | SKU: RSN-INTEL-N59 | Prijs: EUR 5.629,00
Product: White Shark Sagramore | SKU: SAGRAMORE | Prijs: EUR 21,99"""


class Tools:
    def __init__(self):
        pass

    def zoek_pc_prijs(
        self,
        lijn: str = "",
        cpu: str = "",
        gpu: str = "",
        sku: str = "",
    ) -> str:
        """
        Zoek de actieprijs van een Redux Gaming PC op basis van productlijn, CPU, GPU of SKU.
        :param lijn: Productlijn (bijv. Supernova, Nova, Nighthawk, Hyperion)
        :param cpu: CPU naam (bijv. Intel Core Ultra 7 265K, AMD Ryzen 7 9800X3D)
        :param gpu: GPU naam (bijv. RTX 5070 12GB TUF, RX 9070 16GB)
        :param sku: Exacte SKU code (bijv. RSN-INTEL-N57)
        :return: Productinformatie met prijs
        """
        filters = {
            "Lijn": lijn.lower().strip(),
            "CPU": cpu.lower().strip(),
            "GPU": gpu.lower().strip(),
            "SKU": sku.lower().strip(),
        }
        matches = []
        for line in PRODUCTS_DATA.strip().split("\n\n"):
            line = line.strip()
            if not line:
                continue
            line_lower = line.lower()
            score = 0
            for key, val in filters.items():
                if val and val in line_lower:
                    score += 1
            if score > 0:
                matches.append((score, line))
        if not matches:
            return "Geen model gevonden met deze specs. Controleer de productlijn, CPU, GPU of SKU."
        matches.sort(key=lambda x: x[0], reverse=True)
        return "\n\n".join(m[1] for m in matches[:3])

    def zoek_product_prijs(self, naam: str = "", sku: str = "") -> str:
        """
        Zoek de prijs van een accessoire, controller, headset, muis, toetsenbord, monitor of abonnement bij Redux Gaming.
        Gebruik dit voor niet-PC producten: ASUS ROG Raikiri, Logitech G Pro, Endorfy keyboards, monitoren, muismatten, abonnementen, etc.
        :param naam: (deel van) productnaam (bijv. Raikiri Pro, G Pro X Superlight, Endorfy Gem, Logitech G305)
        :param sku: Exacte SKU code
        :return: Productinformatie met prijs
        """
        if not naam and not sku:
            return "Geef een productnaam of SKU op."
        matches = []
        for line in ACCESSOIRES_DATA.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            line_lower = line.lower()
            score = 0
            if naam and naam.lower() in line_lower:
                score += 3
            if naam:
                for word in naam.lower().split():
                    if len(word) > 3 and word in line_lower:
                        score += 1
            if sku and sku.lower() in line_lower:
                score += 5
            if score > 0:
                matches.append((score, line))
        if not matches:
            return f"Product {naam or sku!r} niet gevonden in de Redux Gaming catalogus."
        matches.sort(key=lambda x: x[0], reverse=True)
        return "\n".join(m[1] for m in matches[:5])
