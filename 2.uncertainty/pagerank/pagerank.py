import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    if page not in corpus:
        raise ValueError("Page not in corpus")
    else:
        page_dict = {}
        page_link = corpus[page]
        num_links = len(page_link)
        num_page = len(corpus)


        if num_links == 0:
            for p in corpus.keys():
                page_dict[p] = 1 / num_page
        else:
            p_href = damping_factor / num_links
            p_all_page = (1 - damping_factor) / num_page
            for p in corpus:
                if p in page_link:
                    page_dict[p] = p_href + p_all_page
                else:
                    page_dict[p] = p_all_page

    # 减小误差
    if abs(1-sum(page_dict.values())) > 0.0001:
        raise ValueError("Sum of PR_dict is not 1")
    return page_dict




def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # 为每个页面初始化 samples value
    page_range = {page: 0 for page in corpus.keys()}
    # num_page = len(corpus)
    # 随机选择一个页面
    curr_page = random.choice(list(corpus.keys()))
    page_range[curr_page] += 1

    for _ in range(1, n):
        # 通过转移模型选择下一个页面
        next_page = transition_model(corpus, curr_page, damping_factor)
        # 没有链接的页面，随机选择下一个页面
        if next_page == {}:
            next_page = random.choice(list(corpus.keys()))
        else:
            next_page = random.choices(list(next_page.keys()), weights=list(next_page.values()), k=1)[0]

        page_range[next_page] += 1
        curr_page = next_page
    # calculate the PR
    for page in page_range:
        page_range[page] /= n
    return page_range



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # num_pages = len(corpus)
    # PR_dict = dict()
    # # 初始化PR
    # for page in corpus.keys():
    #     PR_dict[page] = 1 / num_pages
    # # 重复计算直到不超过.001
    # while True:
    #     PR_dict_copy = PR_dict.copy()
    #     for page_i in PR_dict:
    #         PR_dict[page_i] = (1 - damping_factor) / num_pages
    #         for page_p in corpus:
    #             # 如果页面p链接到页面i
    #             if page_i in corpus[page_p]:
    #                 PR_dict[page_i] += damping_factor * PR_dict_copy[page_p] / len(corpus[page_p])
    #     # 如果PR_dict和PR_dict_copy的差异小于0.001，停止迭代
    #     if all(abs(PR_dict[page] - PR_dict_copy[page]) < 0.001 for page in PR_dict):
    #         break
    # return PR_dict
    num_pages = len(corpus)
    PR_dict = {page: 1 / num_pages for page in corpus}

    # 处理没有出链接的页面，假设它们链接到所有页面
    for page in corpus:
        if not corpus[page]:
            corpus[page] = set(corpus.keys())

    while True:
        PR_dict_copy = PR_dict.copy()
        change = False  # 用于检查是否有任何PageRank值的变化超过了0.001
        for page_i in PR_dict:
            rank_sum = 0
            for page_p in corpus:
                if page_i in corpus[page_p]:
                    rank_sum += PR_dict_copy[page_p] / len(corpus[page_p])
            new_rank = (1 - damping_factor) / num_pages + (damping_factor * rank_sum)

            # 检查变化是否超过0.001
            if abs(new_rank - PR_dict[page_i]) > 0.001:
                change = True
            PR_dict[page_i] = new_rank

        # 如果没有任何变化超过0.001，停止迭代
        if not change:
            break

    # 正规化PageRank值以确保它们的总和为1
    total_rank = sum(PR_dict.values())
    for page in PR_dict:
        PR_dict[page] /= total_rank

    return PR_dict


if __name__ == "__main__":
    main()
