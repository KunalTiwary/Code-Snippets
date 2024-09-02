import collections
import heapq
from collections import deque
from copy import deepcopy


class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


    #      5
    #    /   \
    #   2     7
    #  / \   / \
    # 1   3 6   9


# Inorder(left-root-right) -> 1, 2, 3, 5, 6, 7, 9
# PreOrder(root-left-right) -> 5, 2, 1, 3, 7, 6, 9
# PostOrder(left-right-root) -> 1, 3, 2, 6, 9, 7, 5

# tree = TreeNode(5)
# tree.left = TreeNode(2)
# tree.left.left = TreeNode(1)
# tree.left.right = TreeNode(3)
# tree.right = TreeNode(7)
# tree.right.right = TreeNode(9)
# tree.right.left = TreeNode(6)


#
#
# def in_order_rec(root, res):
#     if root is None:
#         return
#     in_order_rec(root.left, res)
#     res.append(root.value)
#     in_order_rec(root.right, res)
#     return res
#
# def pre_order_rec(root, res):
#     if root is None:
#         return
#     res.append(root.value)
#     pre_order_rec(root.left, res)
#     pre_order_rec(root.right, res)
#     return res
#
#
# def post_order_rec(root, res):
#     if root is None:
#         return
#     post_order_rec(root.left, res)
#     post_order_rec(root.right, res)
#     res.append(root.value)
#     return res

# def in_order_iterative(root, res):
#     stack = []
#     while True:
#         if root is not None:
#             stack.append(root)
#             root = root.left
#         elif stack:
#             root = stack.pop()
#             res.append(root.value)
#             root = root.right
#         else:
#             break
#     return res


# def pre_order_iterative(root, res):
#     stack = []
#     while True:
#         if root is not None:
#             stack.append(root)
#             res.append(root.value)
#             root = root.left
#         elif stack:
#             root = stack.pop()
#             root = root.right
#         else:
#             break
#     return res

#      5
#    /   \
#   2     7
#  / \   / \
# 1   3 6   9
# def post_order_iterative(root, res):
#     stack = []
#     while True:
#         if root:
#             stack.append(root)
#             root = root.left
#         elif stack:
#             temp = stack[-1].right
#             if not temp:
#                 temp = stack.pop()
#                 res.append(temp.value)
#                 while stack and temp == stack[-1].right:
#                     temp = stack.pop()
#                     res.append(temp.value)
#             else:
#                 root = temp
#         else:
#             break
#     return res


root = TreeNode(1)
root.left = TreeNode(2)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)
root.right = TreeNode(3)
root.right.right = TreeNode(7)
root.right.left = TreeNode(6)



class Solution:
    def constructFromPrePost(self, preorder, postorder):
        leftPreOrder, leftPostOrder, rightPreOrder, rightPostOrder = [], [], [], []
        if not preorder or not postorder:
            return
        root = TreeNode(preorder.pop(0))
        postorder.pop()
        for i in range(len(postorder)):
            if postorder[i] == preorder[0]:
                leftPreOrder = preorder[:i+1]
                rightPreOrder = preorder[i+1:]
                leftPostOrder = postorder[:i+1]
                rightPostOrder = postorder[i+1:]
                break
        root.left = self.constructFromPrePost(leftPreOrder, leftPostOrder)
        root.right = self.constructFromPrePost(rightPreOrder, rightPostOrder)
        return root

s1 = Solution()
print(s1.constructFromPrePost([1,2,4,5,3,6,7], [4,5,2,6,7,3,1]))