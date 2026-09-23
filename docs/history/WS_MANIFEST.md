# Workshop manifest: who builds what

All names are `SM_VK_*`. They are listed in priority order, and later items may be skipped if time runs out. Your builders may **reference other agents' pieces by name**, but only through a fallback helper, because those pieces may not exist yet while you work:

```python
def <prefix>_pick(name, fallback): return name if bpy.data.objects.get(name) else fallback
```

The fallback must be an existing kit piece or one of your own.

Spec references point to `code/full_judge_buildings.md`.

## humble (prefix `hum_`)
- **Spec:** §6 M3 "Wattle" table, `RoofThatch_Gable_Cruck`, `RoofThatch_Vent` (M2) and the livestock row (M3); §7 Hovel / Longhouse; §8 pig sty / sheepfold.
- **Walls:** Wall_Wattle, Wall_Wattle_Window, Wall_Wattle_Door, Wall_Wattle_Byre, Wall_Wattle_Frame, Corner_Wattle, InnerCorner_Wattle.
- **Roofs and shelters:** RoofThatch_Gable_Cruck, RoofThatch_Vent, LeanTo_Thatch.
- **Animals:** Animal_Cow, Animal_Sheep, Animal_Pig, Animal_Goat, Animal_Horse, Animal_Chickens.
- **Props:** Prop_HayRack, Prop_ChickenCoop.
- **Builders:** `build_hovel(coll, origin, seed=0, variant="cruck")`, `build_longhouse(coll, origin, seed=0)`, `build_pigsty(coll, origin, seed=0)`, `build_sheepfold(coll, origin, seed=0)`.

## frontier (prefix `fro_`)
- **Spec:** §6 M3 "Log", "Shed and open bays" and the S roof family; §7 Log cabin; §8 woodcutter, forester, granary, storehouse.
- **Log walls:** Wall_Log, Wall_Log_Window, Wall_Log_Door, Wall_Log_B, Wall_Log_B_Window, Wall_Log_B_Door, Corner_Log, Roof_Gable_Logs.
- **Shed walls:** Wall_Shed, Wall_Shed_Door, Wall_Shed_Wide, Wall_Shed_Window, Corner_Shed.
- **Open bays:** Wall_Posts, Wall_Posts_Barn, Corner_Posts, Corner_Posts_Barn, Ceiling_Cell.
- **S roofs:** RoofS_Mid, RoofS_Gable, RoofS_Gable_Planks, RoofS_Single, RoofThatchS_Mid, RoofThatchS_Gable, RoofThatchS_Single.
- **Granary props:** Prop_StaddleStone, Prop_GranaryStep.
- **Builders:** `build_logcabin(coll, origin, seed=0, n=2)`, `build_woodcutter(coll, origin, seed=0)`, `build_forester_hut(coll, origin, seed=0)`, `build_granary(coll, origin, seed=0)`, `build_storehouse(coll, origin, seed=0)`.

## construction (prefix `con_`)
- **Spec:** §6 M1 (whole table) and §5.7 stages; the camp and early props from M3; §7 Settler camp; §8 stockpile yard and sawpit.
- **Site and foundations:** BuildSite_Cell, Foundation_Wall, Foundation_Corner.
- **Part-built walls:** Wall_Stone_Half, Wall_Stone_Half_Door, Corner_Stone_Half, Wall_Plaster_Frame, Wall_Plaster_Frame_Door, Wall_Timber_Frame.
- **Roof frames:** Roof_Mid_Frame, Roof_Gable_Frame, Roof_Hip_Frame.
- **Scaffolding:** Scaffold_Wall, Scaffold_Corner, Scaffold_Ladder.
- **Tools:** Prop_Wheelbarrow, Prop_MortarTub, Prop_LadderLean, Prop_ShearLegs.
- **Piles:** Pile_Logs_1/2/3, Pile_Planks_1/2/3, Pile_Stone_1/2/3, Pile_Sacks_1/2/3, Stockpile_Border.
- **Camp:** Tent_A, Tent_Bell, Prop_Campfire, Prop_Bedroll, Prop_Wagon_Covered.
- **Workyard:** Prop_ChoppingBlock, Prop_Sawhorse, Prop_SawPit, Prop_Privy, Prop_WaysideShrine.
- **Builders:** `build_construction_site(coll, origin, stage, seed=0)` for a 3×2 two-storey stone/timber cottage at stage 0/1/2, `build_camp(coll, origin, seed=0)`, `build_stockpile(coll, origin, w=2, d=2, seed=0)`, `build_sawpit_yard(coll, origin, seed=0)`.

## skyline (prefix `sky_`)
- **Spec:** §6 M2 (whole table); from M4: Roof_Mid_CapL/R, Roof_HalfHip, RoofThatch_HalfHip, Roof_CrossGable, Roof_Mid_Hatch, Roof_Mid_Skylight, Roof_Bellcote.
- **Roofs:** Roof_Single, RoofThatch_Single, Roof_Hip_Plain.
- **Chimneys and vents:** Chimney_Gable_H30, Chimney_Gable_H58, Chimney_Gable_H24, Chimney_Party, Roof_Vent.
- **Gable ends:** Roof_Gable_Flush, Roof_Firewall, Roof_Gable_Stepped, Roof_Gable_Hoist, Roof_HalfHip, RoofThatch_HalfHip, Roof_CrossGable.
- **Roof extras:** Roof_Mid_CapL, Roof_Mid_CapR, Roof_Mid_Hatch, Roof_Mid_Skylight, Roof_Bellcote.
- **Emblems:** Emblem_Ridge_{Anvil, Pretzel, Tankard, Fish, Key, Sheaf, Horseshoe, Shield, Book, Axe}.
- **Banners and bunting:** Banner_Wall, Banner_Pole, Banner_Roof, Prop_Bunting_6, Prop_Bunting_9.
- **Builder:** `build_skyline_street(coll, origin, seed=0)`, a street of 6–8 varied houses made from existing walls plus the new roofs, chimneys, emblems and slate/shingle styles, showing that the "field of orange wedges" is gone.

## town (prefix `twn_`)
- **Spec:** §6 M4 (walls, shops, galleries, turret, passage, stairs); §7 merchant house, gable-front townhouse, corner house, terrace.
- **Stone upper floors:** Wall_StoneUp, Wall_StoneUp_Window, Wall_StoneUp_Twin, Wall_StoneUp_Slit, Wall_StoneUp_Loading, Wall_StoneUp_Door, Corner_StoneUp, InnerCorner_StoneUp.
- **Plaster upper floors:** Wall_PlasterUp, Wall_PlasterUp_Window, Wall_PlasterUp_Oxeye, Corner_PlasterUp, InnerCorner_PlasterUp.
- **Shops:** Wall_Stone_Shop, Wall_Plaster_Shop, Prop_ShopGoods_{Bread, Produce, Cloth, Pots, Tools, Meat, Candles, Fish}, Roof_Pent.
- **Passages and galleries:** Wall_Stone_Passage, Passage_Vault, Gallery_Timber, Gallery_End.
- **Turret:** Turret_Corbel, Turret_Seg, Turret_Seg_Stone, Turret_Cap.
- **Steps:** Stoop_Stone, Stair_Stone_Ext, Prop_CellarHatch.
- **Builders:** `build_merchant_house(coll, origin, seed=0)`, `build_townhouse_gablefront(coll, origin, seed=0)`, `build_corner_house(coll, origin, seed=0)`, `build_terrace(coll, origin, units=4, seed=0)`.

## water (prefix `wat_`)
- **Spec:** §6 M5 (whole table); §8 watermill, fisher's hut, smokehouse, lavoir, bridges and quays; §9 water datum.
- **Piers:** Pier_Deck, Pier_End, Pier_Stairs, Pier_Rail.
- **Boats:** Prop_Rowboat, Prop_Barge.
- **Wooden bridges:** Bridge_Wood_Mid, Bridge_Wood_End, Bridge_Wood_Bent.
- **Stone bridges:** Bridge_Stone_Span, Bridge_Stone_Ramp, Bridge_Stone_Pier, Bridge_Log.
- **Quays:** Quay_Straight, Quay_Post, Quay_Stair.
- **Mill:** WaterWheel, Wall_Stone_Axle, Mill_WheelPier, Prop_Millstone.
- **Fishing:** Prop_NetRack, Prop_FishRack, Prop_Creels, Pile_Fish_1/2/3.
- **Washing and water supply:** Prop_LavoirBasin, Prop_WallFountain, Prop_HandPump.
- **Builders:** `build_watermill(coll, origin, seed=0)`, `build_fisher_hut(coll, origin, seed=0)`, `build_smokehouse(coll, origin, seed=0)`, `build_lavoir(coll, origin, seed=0)`, `build_riverside_demo(coll, origin, seed=0)`.
- **Stand-in terrain:** make your own riverbank and water plane at −0.6 inside your assembly, from simple boxes plus a WATER quad.

## industry (prefix `ind_`)
- **Spec:** §6 M6 (all groups except Crops); §8 production features.
- **Mine:** Mine_Portal, Rail_Straight, Rail_Curve, Rail_End, Prop_Minecart, Pile_Ore_1/2/3, Pile_Coal_1/2/3.
- **Quarry:** Quarry_Face_Straight, Quarry_Face_Corner, Quarry_Floor, Prop_Banker, Prop_TreadwheelCrane.
- **Iron:** Prop_CharcoalMound, Prop_Bloomery, Prop_Bellows.
- **Clay:** Prop_BottleKiln, Prop_ClayPit, Prop_PottersWheel, Pile_Bricks_1/2/3.
- **Leather and cloth:** Prop_TanningPit, Prop_HideFrame, Prop_DyeVat, Prop_ClothRack, Prop_Loom, Prop_SpinningWheel, Pile_Hides_1/2/3, Pile_Wool_1/2/3.
- **Food:** Kiln_Oast, Prop_MashTun, Prop_CiderPress, Prop_Skep, Prop_BeeBench, Prop_HerbBundles, Prop_Cauldron, Prop_DryingRack_Meat, Prop_DryingRack_Herbs, Prop_Dovecote.
- **Builders:** `build_mine(coll, origin, seed=0)`, `build_quarry_yard(coll, origin, seed=0)`, `build_charcoal_burner(coll, origin, seed=0)`, `build_tannery(coll, origin, seed=0)`, `build_dyers_yard(coll, origin, seed=0)`, `build_brewery(coll, origin, seed=0)`, `build_apiary(coll, origin, seed=0)`, `build_pottery(coll, origin, seed=0)`.

## defence (prefix `def_`)
- **Spec:** §6 M7 and M8; §7 tower house; §8 palisade → town wall, barracks yard, festival green.
- **Palisade:** Palisade_Straight, Palisade_Diag, Palisade_Post, Palisade_Walk, Palisade_Gate, Palisade_GateLeaf, Palisade_Tower, Prop_Beacon.
- **Town wall:** TownWall_Straight, TownWall_Corner_Out, TownWall_Corner_In, TownWall_Stair, TownWall_Step, TownWall_Ruin, TownWall_Tower_Round, Gatehouse_Block, Gatehouse_Portcullis, Gatehouse_GateLeaf.
- **Parapets and roofs:** Parapet_Crenel, Parapet_Corner, Roof_Pyramid_6, Roof_Cone_R2.
- **Training:** Prop_TrainingDummy, Prop_ArcheryButt, Prop_ArmorStand.
- **Civic:** Prop_MarketCross, Prop_Maypole, Prop_Stage, Prop_Stocks, Prop_Pillory, LowWall_GateArch, Deco_Hedge.
- **Builders:** `build_palisade_demo(coll, origin, seed=0)`, `build_townwall_demo(coll, origin, seed=0)`, `build_tower_house(coll, origin, kind="fortified", seed=0)`, `build_training_yard(coll, origin, seed=0)`, `build_festival_green(coll, origin, seed=0)`.
