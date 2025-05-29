"""
Markdown to ADF (Atlassian Document Format) converter.
Contains the MarkdownToADFConverter class that converts Markdown content to ADF JSON structure.
"""

from typing import Dict, List, Any
from markdown_it import MarkdownIt
from markdown_it.token import Token


class MarkdownToADFConverter:
    """Converts Markdown content to Atlassian Document Format (ADF)."""
    
    def __init__(self):
        # Initialize markdown-it with commonmark preset for consistency
        self.md = MarkdownIt("commonmark", {
            "typographer": True,  # Enable smart quotes, etc.
            "linkify": True,      # Auto-detect URLs
            "html": False,        # Disable raw HTML for security
        })
        
    def convert(self, markdown_content: str) -> Dict[str, Any]:
        """Convert Markdown content to ADF JSON structure."""
        tokens = self.md.parse(markdown_content)
        
        # Create root ADF document
        adf_doc = {
            "version": 1,
            "type": "doc",
            "content": []
        }
        
        # Process tokens into ADF nodes
        adf_doc["content"] = self._process_tokens(tokens)
        
        return adf_doc
    
    def _process_tokens(self, tokens: List[Token]) -> List[Dict[str, Any]]:
        """Process a list of markdown-it tokens into ADF nodes."""
        content = []
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == "heading_open":
                # Process heading
                heading_node, consumed = self._process_heading(tokens, i)
                content.append(heading_node)
                i += consumed
            elif token.type == "paragraph_open":
                # Process paragraph
                paragraph_node, consumed = self._process_paragraph(tokens, i)
                content.append(paragraph_node)
                i += consumed
            elif token.type == "bullet_list_open":
                # Process bullet list
                list_node, consumed = self._process_bullet_list(tokens, i)
                content.append(list_node)
                i += consumed
            elif token.type == "ordered_list_open":
                # Process ordered list
                list_node, consumed = self._process_ordered_list(tokens, i)
                content.append(list_node)
                i += consumed
            elif token.type == "blockquote_open":
                # Process blockquote
                quote_node, consumed = self._process_blockquote(tokens, i)
                content.append(quote_node)
                i += consumed
            elif token.type == "fence":
                # Process code block (fenced)
                code_node = self._process_code_block(token)
                content.append(code_node)
                i += 1
            elif token.type == "code_block":
                # Process code block (indented)
                code_node = self._process_code_block(token)
                content.append(code_node)
                i += 1
            elif token.type == "table_open":
                # Process table
                table_node, consumed = self._process_table(tokens, i)
                content.append(table_node)
                i += consumed
            elif token.type == "hr":
                # Process horizontal rule
                content.append({"type": "rule"})
                i += 1
            else:
                # Skip unprocessed tokens
                i += 1
                
        return content
    
    def _process_heading(self, tokens: List[Token], start_idx: int) -> tuple[Dict[str, Any], int]:
        """Process heading tokens into ADF heading node."""
        open_token = tokens[start_idx]
        level = int(open_token.tag[1])  # Extract level from h1, h2, etc.
        
        # Find inline content
        inline_content = []
        consumed = 1
        
        for i in range(start_idx + 1, len(tokens)):
            token = tokens[i]
            if token.type == "heading_close":
                consumed = i - start_idx + 1
                break
            elif token.type == "inline":
                inline_content = self._process_inline_content(token)
            
        return {
            "type": "heading",
            "attrs": {"level": level},
            "content": inline_content
        }, consumed
    
    def _process_paragraph(self, tokens: List[Token], start_idx: int) -> tuple[Dict[str, Any], int]:
        """Process paragraph tokens into ADF paragraph node."""
        inline_content = []
        consumed = 1
        
        for i in range(start_idx + 1, len(tokens)):
            token = tokens[i]
            if token.type == "paragraph_close":
                consumed = i - start_idx + 1
                break
            elif token.type == "inline":
                inline_content = self._process_inline_content(token)
                
        return {
            "type": "paragraph",
            "content": inline_content
        }, consumed
    
    def _process_bullet_list(self, tokens: List[Token], start_idx: int) -> tuple[Dict[str, Any], int]:
        """Process bullet list tokens into ADF bulletList node."""
        list_items = []
        consumed = 1
        i = start_idx + 1
        
        while i < len(tokens):
            token = tokens[i]
            if token.type == "bullet_list_close":
                consumed = i - start_idx + 1
                break
            elif token.type == "list_item_open":
                list_item, item_consumed = self._process_list_item(tokens, i)
                list_items.append(list_item)
                i += item_consumed
            else:
                i += 1
                
        return {
            "type": "bulletList",
            "content": list_items
        }, consumed
    
    def _process_ordered_list(self, tokens: List[Token], start_idx: int) -> tuple[Dict[str, Any], int]:
        """Process ordered list tokens into ADF orderedList node."""
        open_token = tokens[start_idx]
        list_items = []
        consumed = 1
        i = start_idx + 1
        
        # Extract start number if present
        attrs = {}
        if hasattr(open_token, 'attrGet') and open_token.attrGet('start'):
            attrs["order"] = int(open_token.attrGet('start'))
        
        while i < len(tokens):
            token = tokens[i]
            if token.type == "ordered_list_close":
                consumed = i - start_idx + 1
                break
            elif token.type == "list_item_open":
                list_item, item_consumed = self._process_list_item(tokens, i)
                list_items.append(list_item)
                i += item_consumed
            else:
                i += 1
                
        node = {
            "type": "orderedList",
            "content": list_items
        }
        if attrs:
            node["attrs"] = attrs
            
        return node, consumed
    
    def _process_list_item(self, tokens: List[Token], start_idx: int) -> tuple[Dict[str, Any], int]:
        """Process list item tokens into ADF listItem node."""
        item_content = []
        consumed = 1
        i = start_idx + 1
        
        while i < len(tokens):
            token = tokens[i]
            if token.type == "list_item_close":
                consumed = i - start_idx + 1
                break
            elif token.type == "paragraph_open":
                paragraph, para_consumed = self._process_paragraph(tokens, i)
                item_content.append(paragraph)
                i += para_consumed
            elif token.type in ["bullet_list_open", "ordered_list_open"]:
                # Nested list
                if token.type == "bullet_list_open":
                    nested_list, nested_consumed = self._process_bullet_list(tokens, i)
                else:
                    nested_list, nested_consumed = self._process_ordered_list(tokens, i)
                item_content.append(nested_list)
                i += nested_consumed
            else:
                i += 1
                
        return {
            "type": "listItem",
            "content": item_content
        }, consumed
    
    def _process_blockquote(self, tokens: List[Token], start_idx: int) -> tuple[Dict[str, Any], int]:
        """Process blockquote tokens into ADF blockquote node."""
        quote_content = []
        consumed = 1
        i = start_idx + 1
        
        while i < len(tokens):
            token = tokens[i]
            if token.type == "blockquote_close":
                consumed = i - start_idx + 1
                break
            elif token.type == "paragraph_open":
                paragraph, para_consumed = self._process_paragraph(tokens, i)
                quote_content.append(paragraph)
                i += para_consumed
            else:
                i += 1
                
        return {
            "type": "blockquote",
            "content": quote_content
        }, consumed
    
    def _process_code_block(self, token: Token) -> Dict[str, Any]:
        """Process code block token into ADF codeBlock node."""
        # Extract language from info string (for fenced code blocks)
        language = None
        if hasattr(token, 'info') and token.info:
            language = token.info.strip().split()[0]  # Take first word as language
            
        node = {
            "type": "codeBlock",
            "content": [
                {
                    "type": "text",
                    "text": token.content.rstrip('\n')  # Remove trailing newline
                }
            ]
        }
        
        if language:
            node["attrs"] = {"language": language}
            
        return node
    
    def _process_table(self, tokens: List[Token], start_idx: int) -> tuple[Dict[str, Any], int]:
        """Process table tokens into ADF table node."""
        table_rows = []
        consumed = 1
        i = start_idx + 1
        
        while i < len(tokens):
            token = tokens[i]
            if token.type == "table_close":
                consumed = i - start_idx + 1
                break
            elif token.type in ["thead_open", "tbody_open"]:
                # Process table sections
                i += 1
                continue
            elif token.type in ["thead_close", "tbody_close"]:
                i += 1
                continue
            elif token.type == "tr_open":
                row, row_consumed = self._process_table_row(tokens, i)
                table_rows.append(row)
                i += row_consumed
            else:
                i += 1
                
        return {
            "type": "table",
            "attrs": {
                "isNumberColumnEnabled": False,
                "layout": "center"
            },
            "content": table_rows
        }, consumed
    
    def _process_table_row(self, tokens: List[Token], start_idx: int) -> tuple[Dict[str, Any], int]:
        """Process table row tokens into ADF tableRow node."""
        row_cells = []
        consumed = 1
        i = start_idx + 1
        is_header_row = False
        
        while i < len(tokens):
            token = tokens[i]
            if token.type == "tr_close":
                consumed = i - start_idx + 1
                break
            elif token.type in ["th_open", "td_open"]:
                is_header = token.type == "th_open"
                if is_header:
                    is_header_row = True
                cell, cell_consumed = self._process_table_cell(tokens, i, is_header)
                row_cells.append(cell)
                i += cell_consumed
            else:
                i += 1
                
        return {
            "type": "tableRow",
            "content": row_cells
        }, consumed
    
    def _process_table_cell(self, tokens: List[Token], start_idx: int, is_header: bool) -> tuple[Dict[str, Any], int]:
        """Process table cell tokens into ADF tableCell or tableHeader node."""
        cell_content = []
        consumed = 1
        i = start_idx + 1
        close_type = "th_close" if is_header else "td_close"
        
        # Collect inline content
        inline_tokens = []
        while i < len(tokens):
            token = tokens[i]
            if token.type == close_type:
                consumed = i - start_idx + 1
                break
            elif token.type == "inline":
                inline_tokens.extend(token.children if token.children else [])
            i += 1
        
        # Convert inline tokens to content
        if inline_tokens:
            # Create a temporary inline token to process
            temp_token = Token("inline", "", 0)
            temp_token.children = inline_tokens
            temp_token.content = "".join(t.content for t in inline_tokens if hasattr(t, 'content'))
            cell_content = self._process_inline_content(temp_token)
        
        # Wrap content in a paragraph if not empty
        if cell_content:
            paragraph_content = [{
                "type": "paragraph",
                "content": cell_content
            }]
        else:
            paragraph_content = [{
                "type": "paragraph", 
                "content": [{"type": "text", "text": ""}]
            }]
        
        cell_type = "tableHeader" if is_header else "tableCell"
        return {
            "type": cell_type,
            "attrs": {},
            "content": paragraph_content
        }, consumed
    
    def _process_inline_content(self, token: Token) -> List[Dict[str, Any]]:
        """Process inline token content into ADF inline nodes."""
        if not token.children:
            # Handle simple text content
            if token.content:
                return [{"type": "text", "text": token.content}]
            return []
        
        content = []
        i = 0
        
        while i < len(token.children):
            child = token.children[i]
            
            if child.type == "text":
                content.append({
                    "type": "text",
                    "text": child.content
                })
            elif child.type in ["strong_open", "em_open", "code_inline", "link_open"]:
                inline_node, consumed = self._process_inline_formatting(token.children, i)
                content.append(inline_node)
                i += consumed - 1  # Adjust for consumed tokens
            elif child.type == "softbreak":
                content.append({"type": "text", "text": " "})
            elif child.type == "hardbreak":
                content.append({"type": "hardBreak"})
            
            i += 1
            
        return content
    
    def _process_inline_formatting(self, children: List[Token], start_idx: int) -> tuple[Dict[str, Any], int]:
        """Process inline formatting tokens into ADF text nodes with marks."""
        start_token = children[start_idx]
        consumed = 1
        text_content = ""
        marks = []
        
        if start_token.type == "strong_open":
            marks.append({"type": "strong"})
            close_type = "strong_close"
        elif start_token.type == "em_open":
            marks.append({"type": "em"})
            close_type = "em_close"
        elif start_token.type == "code_inline":
            # Inline code is self-contained
            return {
                "type": "text",
                "text": start_token.content,
                "marks": [{"type": "code"}]
            }, 1
        elif start_token.type == "link_open":
            href = start_token.attrGet("href") if hasattr(start_token, 'attrGet') else "#"
            marks.append({"type": "link", "attrs": {"href": href}})
            close_type = "link_close"
        else:
            # Fallback
            return {"type": "text", "text": start_token.content}, 1
        
        # Collect content until closing token
        for i in range(start_idx + 1, len(children)):
            token = children[i]
            if token.type == close_type:
                consumed = i - start_idx + 1
                break
            elif token.type == "text":
                text_content += token.content
                
        return {
            "type": "text",
            "text": text_content,
            "marks": marks
        }, consumed 