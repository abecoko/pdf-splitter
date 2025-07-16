export interface ParseRangeResult {
  isValid: boolean;
  error?: string;
  pages?: number[];
}

export function parsePageRanges(rangeStr: string): ParseRangeResult {
  if (!rangeStr.trim()) {
    return {
      isValid: false,
      error: "Page ranges cannot be empty"
    };
  }

  try {
    const pages = new Set<number>();
    const ranges = rangeStr.split(',');

    for (const range of ranges) {
      const trimmedRange = range.trim();
      if (!trimmedRange) continue;

      if (trimmedRange.includes('-')) {
        // Range like "1-5"
        const parts = trimmedRange.split('-');
        if (parts.length !== 2) {
          return {
            isValid: false,
            error: `Invalid range format: ${trimmedRange}`
          };
        }

        const start = parseInt(parts[0].trim());
        const end = parseInt(parts[1].trim());

        if (isNaN(start) || isNaN(end)) {
          return {
            isValid: false,
            error: `Invalid page numbers in range: ${trimmedRange}`
          };
        }

        if (start < 1 || end < 1) {
          return {
            isValid: false,
            error: "Page numbers must be positive"
          };
        }

        if (start > end) {
          return {
            isValid: false,
            error: `Invalid range: ${trimmedRange} (start > end)`
          };
        }

        for (let i = start; i <= end; i++) {
          pages.add(i);
        }
      } else {
        // Single page like "5"
        const pageNum = parseInt(trimmedRange);
        if (isNaN(pageNum)) {
          return {
            isValid: false,
            error: `Invalid page number: ${trimmedRange}`
          };
        }

        if (pageNum < 1) {
          return {
            isValid: false,
            error: "Page numbers must be positive"
          };
        }

        pages.add(pageNum);
      }
    }

    if (pages.size === 0) {
      return {
        isValid: false,
        error: "No valid pages specified"
      };
    }

    return {
      isValid: true,
      pages: Array.from(pages).sort((a, b) => a - b)
    };
  } catch (error) {
    return {
      isValid: false,
      error: "Invalid page range format"
    };
  }
}

export function validatePageRangesWithTotal(rangeStr: string, totalPages: number): ParseRangeResult {
  const result = parsePageRanges(rangeStr);
  
  if (!result.isValid || !result.pages) {
    return result;
  }

  const outOfBoundsPages = result.pages.filter(page => page > totalPages);
  if (outOfBoundsPages.length > 0) {
    return {
      isValid: false,
      error: `Page(s) ${outOfBoundsPages.join(', ')} are out of bounds (PDF has ${totalPages} pages)`
    };
  }

  return result;
}

export function formatPageRanges(pages: number[]): string {
  if (pages.length === 0) return '';
  
  const groups: string[] = [];
  let start = pages[0];
  let end = pages[0];
  
  for (let i = 1; i < pages.length; i++) {
    if (pages[i] === end + 1) {
      end = pages[i];
    } else {
      if (start === end) {
        groups.push(start.toString());
      } else {
        groups.push(`${start}-${end}`);
      }
      start = pages[i];
      end = pages[i];
    }
  }
  
  if (start === end) {
    groups.push(start.toString());
  } else {
    groups.push(`${start}-${end}`);
  }
  
  return groups.join(',');
}

export function getPageRangeExamples(): string[] {
  return [
    "1-5",
    "1-3,5",
    "1,3,5-7",
    "1-5,8,10-12",
    "2,4,6-10,15"
  ];
}