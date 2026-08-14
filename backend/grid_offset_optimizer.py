# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

import numpy as np

def get_offset_candidates(cell_w, min_cell_w):
    """Returns grid of offset factors [0.0, 1.0)"""
    if cell_w < 5.0 * min_cell_w:
        # Fine scale: 4x4 offsets
        offsets = np.linspace(0, 0.75, 4)
    elif cell_w < 20.0 * min_cell_w:
        # Medium scale: 3x3 offsets
        offsets = np.linspace(0, 0.66, 3)
    else:
        # Coarse scale: 2x2 offsets
        offsets = np.linspace(0, 0.5, 2)

    # Generate 2D grid of offsets
    ox, oy = np.meshgrid(offsets, offsets)
    return np.stack([ox.ravel(), oy.ravel()], axis=1)

def prune_candidate_cells(rows, cols, filled_mask, grid_rows, grid_cols):
    """
    Pruning rule: only test shifted cells whose 9-neighborhood in the
    baseline grid contains at least one occupied cell.
    """
    # Create a 2D occupancy mask
    occupancy = np.zeros((grid_rows, grid_cols), dtype=bool)
    occupancy[rows[filled_mask], cols[filled_mask]] = True

    # Pure NumPy implementation of 2D 9-neighborhood binary dilation (3x3 structuring element):
    # Dilate along Y-axis first
    dilated_y = occupancy.copy()
    dilated_y[1:, :] |= occupancy[:-1, :]
    dilated_y[:-1, :] |= occupancy[1:, :]

    # Dilate along X-axis second on top of Y-dilated grid
    dilated_x = dilated_y.copy()
    dilated_x[:, 1:] |= dilated_y[:, :-1]
    dilated_x[:, :-1] |= dilated_y[:, 1:]

    # Return indices of all candidate cells (both filled and empty neighborhood)
    cand_rows, cand_cols = np.where(dilated_x)
    return cand_rows, cand_cols

def optimize_grid_offset(
    bulk_fill_decision_func,
    all_rows, all_cols, all_filled_mask,
    grid_rows, grid_cols, cell_w, cell_h, min_cell_w,
    xmin, ymin,
    fill_tree, fill_objs, stroke_tree, stroke_objs, stroke_widths,
    fill_obj_arr, stroke_obj_arr
):
    """
    Finds the grid offset that minimizes the box count.
    """
    # 1. Baseline count
    best_count = int(all_filled_mask.sum())

    # 2. Identify candidate cells to test (pruning)
    cand_rows, cand_cols = prune_candidate_cells(all_rows, all_cols, all_filled_mask, grid_rows, grid_cols)
    if len(cand_rows) == 0:
        return best_count, all_filled_mask

    # 3. Get offset candidates
    offset_grid = get_offset_candidates(cell_w, min_cell_w)

    best_mask = all_filled_mask

    # We need to map cand_rows/cols back to the full filled_mask
    # Create a mapping from (r, c) to index in all_rows/all_cols
    # Since all_rows/all_cols cover the full grid, the index is r * grid_cols + c
    full_mask_idx = all_rows * grid_cols + all_cols
    mask_map = np.zeros(grid_rows * grid_cols, dtype=np.int32) - 1
    mask_map[full_mask_idx] = np.arange(len(all_rows))

    cand_indices = mask_map[cand_rows * grid_cols + cand_cols]

    # 4. Test offsets
    for ox, oy in offset_grid:
        if ox == 0 and oy == 0: continue # Baseline

        # Shifted coordinates for the candidates
        x0_cand = xmin + (cand_cols.astype(np.float64) + ox) * cell_w
        y0_cand = ymin + (cand_rows.astype(np.float64) + oy) * cell_h
        x1_cand = x0_cand + cell_w
        y1_cand = y0_cand + cell_h

        # Run bulk fill on candidates
        shifted_cand_mask = bulk_fill_decision_func(
            x0_cand, y0_cand, x1_cand, y1_cand,
            fill_tree, fill_objs,
            stroke_tree, stroke_objs, stroke_widths,
            fill_obj_arr, stroke_obj_arr
        )

        count = int(shifted_cand_mask.sum())
        if count < best_count:
            best_count = count

            # Construct the full mask based on best offset
            new_full_mask = all_filled_mask.copy()
            # Set all candidates to False first
            new_full_mask[cand_indices] = False
            # Set the new candidate results
            new_full_mask[cand_indices] = shifted_cand_mask
            best_mask = new_full_mask

    return best_count, best_mask
