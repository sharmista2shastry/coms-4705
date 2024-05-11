#include<vector>
#include<iostream>
#include<queue>
using namespace std;

class TreeNode{
    public:
    int val;
    TreeNode *left, *right;

    TreeNode(){
        this->val = 0;
        left = NULL;
        right = NULL;
    }

    TreeNode(int val){
        this->val = val;
        left = NULL;
        right = NULL;
    }
};

TreeNode* buildTree(vector<TreeNode*>&treeArr, int n){
    for(int i=0; i<n/2; i++)
    {
        if(2*i + 1 < n)
        treeArr[i]->left = treeArr[2*i+1];

        if(2*i + 2 < n)
        treeArr[i]->right = treeArr[2*i+2];
    }

    return treeArr[0];
}

TreeNode* findNode(TreeNode *root, int pos){
    queue<TreeNode*> q;
    q.push(root);

    while(!q.empty()){
        int levelSize = q.size();

        for(int i=0; i<levelSize; i++)
        {
            TreeNode *front = q.front();
            q.pop();

            pos--;

            if(pos == 0)
                return front;
            
            if(front->left)
            q.push(front->left);

            if(front->right)
            q.push(front->right);
        }
    }

    return NULL;
}

void set_bit_subtree(TreeNode *root){
    if(root == NULL)
        return;

    if(root->val == 0)
        root->val = 1;
    
    set_bit_subtree(root->left);
    set_bit_subtree(root->right);
}

void set_bit(TreeNode* root, int pos, int len){
    for(int i=pos; i<=len; i++){
        if(root->val == 1)
        {
            TreeNode *start = findNode(root, i);
            set_bit_subtree(start);
        }
    }

    return;
}

void display(TreeNode *root){
    if(root == NULL)
        return;
    
    cout << root->val << " ";

    display(root->left);
    display(root->right);
}

void clear_bit_subtree(TreeNode *root){
    if(root == NULL)
        return;

    if(root->val == 1)
        root->val = 0;
    
    clear_bit_subtree(root->left);
    clear_bit_subtree(root->right);
}

void clear_bit(TreeNode *root, int pos, int len){
    for(int i=pos; i<=len; i++){
        TreeNode *start = findNode(root, i);
        clear_bit_subtree(start);
    }

    return;
}

int main()
{
    int n;
    cout << "Enter the number of nodes in the tree: " << endl;
    cin >> n;

    if(n == 0)
        return 0;

    vector<TreeNode*> treeArr(n);

    cout << "Enter the values of the nodes: " << endl;
    for(int i=0; i<n; i++){
        int num;
        cin >> num;
        TreeNode *root = new TreeNode(num);
        treeArr[i] = root;
    }

    TreeNode* root = buildTree(treeArr, n);
    cout << "Old Tree: " << endl;
    display(root);
    cout << endl;
    
    int pos, len, choice;

    cout << "Enter offset: " << endl;
    cin >> pos;
    cout << "Enter length: " << endl;
    cin >> len;

    cout << "Enter 1 for setBit API or Enter 2 for clearBit API:: " << endl;
    cin >> choice;

    if(choice == 1)
    set_bit(root, pos, pos + len - 1);

    if(choice == 2)
    clear_bit(root, pos, pos + len - 1);

    cout << "New tree: " << endl;
    display(root);

    return 0;
}