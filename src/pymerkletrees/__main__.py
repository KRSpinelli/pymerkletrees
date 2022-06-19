from treelib import Node, Tree  # type: ignore[import]
import hashlib
import math
from typing import Iterator


def hash_data(data: str) -> str:
    """
    Return SHA256 hash of string
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_combined_hash(first_node: Node, second_node: Node) -> str:
    """
    Create a combined hash from the hashes of two nodes
    """
    # TODO: Determine if this is how hashes are supposed to be combined
    if second_node is None:
        return first_node.tag
    else:
        combined_hash: str = "".join([first_node.tag, second_node.tag])

    return hash_data(combined_hash)


def generate_parent_node(
    first_node: Node, second_node: Node, tree_id: int
) -> Node:
    """
    Generate merkle tree parent node
    """
    parent_hash: str = generate_combined_hash(first_node, second_node)
    parent_node: Node = Node(parent_hash)

    # set forward and backwards node pointers
    parent_node.update_successors(first_node.identifier, tree_id=tree_id)
    first_node.set_predecessor(parent_node.identifier, tree_id)

    if second_node is not None:
        parent_node.update_successors(second_node.identifier, tree_id=tree_id)
        second_node.set_predecessor(parent_node.identifier, tree_id)

    return parent_node


def generate_merkle_tree(data: list) -> Tree:
    """
    Create a merkle tree from a given list
    """
    tree = Tree(node_class=Node)
    hashed_data: list = [Node(hash_data(data_point)) for data_point in data]
    tree_height: int = math.ceil(math.log(len(hashed_data), 2)) + 1
    bottom_level_width: int = pow(2, tree_height - 1)
    filler_items = [None] * (bottom_level_width - len(hashed_data))
    current_level: Iterator = iter(hashed_data + filler_items)

    for node in hashed_data:
        tree._nodes.update({node.identifier: node})
        node.set_initial_tree_id(tree.identifier)

    for level in range(tree_height, 1, -1):
        new_level: list = []

        for node in current_level:
            first_node: Node = node
            second_node: Node = next(current_level)
            new_node: Node = None
            if first_node != None:
                new_node = generate_parent_node(  # type: ignore[no-redef]
                    first_node, second_node, tree.identifier
                )
                tree._nodes.update({new_node.identifier: new_node})
                new_node.set_initial_tree_id(tree.identifier)

            new_level.append(new_node)

        current_level = iter(new_level)
        if len(new_level) == 1:
            tree.root = new_level[0].identifier

    tree.show()

    return tree


generate_merkle_tree(
    [
        "a gives to b",
        "b gives to c",
        "c gives to a",
        "a gives to e",
        "e gives to f",
        "f gives to d",
        "d gives to a",
        "a gives to b",
        "b gives to f",
    ]
)
