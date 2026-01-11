# Sales Attribution Fix - Test Plan

## Changes Made

### 1. Backend (Already Working Correctly)
- ✅ Sales detection runs **only on 5-second snapshot intervals** in `inventory_persistent.py`
- ✅ Sales attribution engine compares consecutive post-smoothing snapshots
- ✅ Each sale records actual `product_name`, `quantity_delta`, `timestamp_utc`, and `timestamp_est`
- ✅ Server broadcasts sales data via WebSocket with type 'sales'

### 2. Frontend (Fixed)
- ✅ **Removed client-side sales detection** (`checkForSales()` function)
- ✅ Added `updateSalesFromServer()` to consume server-side sales data
- ✅ Added 'sales' message handler in WebSocket message switch
- ✅ Display shows actual product names with quantity
- ✅ Uses server-side EST timestamps

### 3. Sales Attribution Logic (Verified)
- ✅ Per-product attribution is always attempted first
- ✅ Product names are the actual class labels from YOLO detection
- ✅ "Unknown" is only used as fallback when total decreased but no specific product attributed
- ✅ Temporal validation requires persistence across `confirm_intervals` (default: 2)

## Test Procedure

### Test 1: No False Positives from Frame Fluctuations
**Steps:**
1. Start the system: `cd "Testing On Pc" && python3 run_pc_webcam.py`
2. Place 5 identical items in camera view
3. Keep them steady for 15 seconds (3 snapshot intervals)
4. Check Sales Log in web interface

**Expected Result:**
- ✅ No sales logged (items stable, no decrease)

### Test 2: Single Item Removal Detection
**Steps:**
1. With 5 items visible, wait for 2 snapshot intervals (10 seconds)
2. Remove exactly 1 item and keep it removed
3. Wait for next snapshot interval (5 seconds)
4. Check Sales Log

**Expected Result:**
- ✅ Exactly **one sale record** appears after 5-10 seconds
- ✅ Shows correct `product_name` (e.g., "mango", "watermelon")
- ✅ Shows `quantity_delta=1` or displays as "(x1)"
- ✅ Timestamp in EST format (e.g., "01/10/2026, 02:30:15 PM EST")

### Test 3: Multiple Items Removal
**Steps:**
1. With 5 items visible, wait for 2 snapshot intervals (10 seconds)
2. Remove 3 items of the same product
3. Wait for confirmation (5-10 seconds)

**Expected Result:**
- ✅ One sale record showing the product with quantity (x3)

### Test 4: Different Products
**Steps:**
1. Place 3 mangos and 2 watermelons
2. Wait 10 seconds for baseline
3. Remove 1 mango
4. Wait 10 seconds
5. Remove 1 watermelon

**Expected Result:**
- ✅ Two separate sale records
- ✅ First: "mango (x1)" with timestamp
- ✅ Second: "watermelon (x1)" with timestamp (10 seconds later)

### Test 5: Verify No "Unknown" When Product Known
**Steps:**
1. Place clearly visible products
2. Remove them one by one
3. Check all sales logs

**Expected Result:**
- ✅ All sales show actual product names
- ✅ No "Unknown" entries (unless detection truly failed)

## Configuration Verification

### PC Testing Config (`Testing On Pc/pc_config.yaml`)
```yaml
inventory:
  smoothing_window: 10             # Frames to average
  smoothing_method: median         # median, mean, or mode
  enable_persistence: true         # Enable SQLite persistence
  snapshot_interval: 5.0           # ✓ 5-second interval
  sales_confirm_intervals: 2       # ✓ Requires 2 intervals
  sales_min_delta: 1               # ✓ Minimum 1 item change
  sales_cooldown_seconds: 10.0     # 10s cooldown between same product
```

### Jetson Production Config (`config/config.yaml`)
Should have same settings for consistency.

## Running the Test

```bash
# Terminal 1: Start system
cd "/Users/felipecardozo/Desktop/coding/Poke-Bowl---updated-January/Testing On Pc"
python3 run_pc_webcam.py

# Browser: Open web interface
# http://localhost:8080

# Monitor the Sales Log section in bottom right panel
```

## Success Criteria

✅ **Correct Cadence**: Sales appear only after 5-second intervals, not per-frame
✅ **Correct Attribution**: Each sale shows actual product name (e.g., "mango", "watermelon")
✅ **Correct Quantity**: Shows quantity if > 1 (e.g., "mango (x3)")
✅ **Correct Timestamp**: Displays in EST format from server
✅ **No False Positives**: Stable inventory = no sales logged
✅ **Temporal Validation**: Requires persistence across 2 intervals (10 seconds total)

## Rollback Plan

If issues occur, the previous behavior can be restored by:
1. Reverting frontend changes in `index.html`
2. Backend persistence layer can be disabled via config: `enable_persistence: false`

## Production Deployment

After successful PC testing:
1. Verify same fix on Jetson with USB camera
2. Ensure `config/config.yaml` has same `snapshot_interval` and `sales_confirm_intervals`
3. Test with actual poke bowl products
4. Monitor logs for any "Unknown" sales (investigate if frequent)
