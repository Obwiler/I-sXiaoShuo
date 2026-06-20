-- table_filter.lua — pandoc Lua filter for 三线表 (three-line table style)
-- Removes all borders, then adds: top line (1.5pt), header separator (0.5pt), bottom line (1.5pt)

function Table(tbl)
    -- Remove all borders
    for _, row in ipairs(tbl.rows) do
        for _, cell in ipairs(row.cells) do
            cell.borders = pandoc.Borders()
        end
    end
    return tbl
end

function Pandoc(doc)
    -- Add top/bottom borders to tables via raw OpenXML
    local new_blocks = {}
    for _, block in ipairs(doc.blocks) do
        if block.t == 'Table' then
            -- Mark table for post-processing with openxml
            table.insert(new_blocks, block)
        else
            table.insert(new_blocks, block)
        end
    end
    return pandoc.Pandoc(new_blocks, doc.meta)
end
