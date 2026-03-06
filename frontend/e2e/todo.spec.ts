import { test, expect, type Page } from "@playwright/test";

// ─── ヘルパー ──────────────────────────────────────────────────────────────

async function addTodo(page: Page, title: string, description?: string) {
  await page.getByPlaceholder("何をしますか？").fill(title);
  if (description) {
    await page.getByPlaceholder("詳細メモ").fill(description);
  }
  await page.getByRole("button", { name: "+ 追加" }).click();
  // 一覧に追加されるまで待機
  await expect(page.getByText(title)).toBeVisible({ timeout: 5000 });
}

// ─── テスト前処理 ──────────────────────────────────────────────────────────

test.beforeEach(async ({ page }) => {
  // バックエンドの todos をリセット（直接 API を叩いて全削除）
  const resp = await page.request.get("http://localhost:8000/api/todos");
  if (resp.ok()) {
    const todos = await resp.json();
    for (const todo of todos) {
      await page.request.delete(`http://localhost:8000/api/todos/${todo.id}`);
    }
  }
  await page.goto("/todos");
});

// ─── 6.2-1: 一覧表示 ──────────────────────────────────────────────────────

test("初期表示: 空のとき「タスクがありません」が表示される", async ({
  page,
}) => {
  await expect(page.getByText("タスクがありません")).toBeVisible();
});

test("Todo 作成後: 一覧に表示される", async ({ page }) => {
  await addTodo(page, "牛乳を買う");
  await expect(page.getByText("牛乳を買う")).toBeVisible();
});

// ─── 6.2-2: 作成 ──────────────────────────────────────────────────────────

test("Todo 作成: タイトル + 説明を入力して追加できる", async ({ page }) => {
  await addTodo(page, "スーパーに行く", "17時以降に");
  await expect(page.getByText("スーパーに行く")).toBeVisible();
  await expect(page.getByText("17時以降に")).toBeVisible();
});

test("Todo 作成: 追加後フォームがリセットされる", async ({ page }) => {
  const titleInput = page.getByPlaceholder("何をしますか？");
  await titleInput.fill("リセット確認");
  await page.getByRole("button", { name: "+ 追加" }).click();
  await expect(page.getByText("リセット確認")).toBeVisible();
  await expect(titleInput).toHaveValue("");
});

test("Todo 作成: タイトルが空のとき追加ボタンが無効", async ({ page }) => {
  const addBtn = page.getByRole("button", { name: "+ 追加" });
  await expect(addBtn).toBeDisabled();
});

test("Todo 作成: 複数追加すると全件表示される", async ({ page }) => {
  await addTodo(page, "タスク A");
  await addTodo(page, "タスク B");
  await expect(page.getByText("タスク A")).toBeVisible();
  await expect(page.getByText("タスク B")).toBeVisible();
});

// ─── 6.2-3: 更新 ──────────────────────────────────────────────────────────

test("Todo 更新: 編集ボタンでインライン編集モードになる", async ({ page }) => {
  await addTodo(page, "編集前タイトル");
  await page.getByRole("button", { name: "編集" }).first().click();
  // 入力フィールドが表示される
  await expect(page.getByRole("button", { name: "保存" })).toBeVisible();
  await expect(page.getByRole("button", { name: "キャンセル" })).toBeVisible();
});

test("Todo 更新: タイトルを変更して保存できる", async ({ page }) => {
  await addTodo(page, "旧タイトル");
  await page.getByRole("button", { name: "編集" }).first().click();

  // タイトル入力欄をクリアして新しい値を入力
  const inputs = page.locator('input[placeholder="タイトル"]');
  await inputs.first().clear();
  await inputs.first().fill("新タイトル");
  await page.getByRole("button", { name: "保存" }).click();

  await expect(page.getByText("新タイトル")).toBeVisible();
  await expect(page.getByText("旧タイトル")).not.toBeVisible();
});

test("Todo 更新: キャンセルで元のタイトルに戻る", async ({ page }) => {
  await addTodo(page, "キャンセル確認");
  await page.getByRole("button", { name: "編集" }).first().click();

  const inputs = page.locator('input[placeholder="タイトル"]');
  await inputs.first().clear();
  await inputs.first().fill("変更後");
  await page.getByRole("button", { name: "キャンセル" }).click();

  await expect(page.getByText("キャンセル確認")).toBeVisible();
  await expect(page.getByText("変更後")).not.toBeVisible();
});

test("Todo 更新: チェックボックスで完了状態をトグルできる", async ({
  page,
}) => {
  await addTodo(page, "完了テスト");
  const checkbox = page.getByRole("checkbox", { name: "完了にする" }).first();
  await expect(checkbox).not.toBeChecked();
  await checkbox.click();
  // aria-label が「未完了に戻す」に変わる＝チェック済みになる
  await expect(
    page.getByRole("checkbox", { name: "未完了に戻す" }).first(),
  ).toBeChecked({ timeout: 5000 });
});

// ─── 6.2-4: 削除 ──────────────────────────────────────────────────────────

test("Todo 削除: 削除ボタンで Todo が消える", async ({ page }) => {
  await addTodo(page, "削除対象");
  await page.getByRole("button", { name: "削除" }).first().click();
  await expect(page.getByText("削除対象")).not.toBeVisible({ timeout: 5000 });
});

test("Todo 削除: 他の Todo は残る", async ({ page }) => {
  await addTodo(page, "残す");
  await addTodo(page, "消す");

  // 「消す」の行の削除ボタンをクリック
  const todoItems = page.locator("li");
  const deleteTarget = todoItems.filter({ hasText: "消す" });
  await deleteTarget.getByRole("button", { name: "削除" }).click();

  await expect(page.getByText("残す")).toBeVisible();
  await expect(page.getByText("消す")).not.toBeVisible({ timeout: 5000 });
});

test("Todo 削除後: 全件削除したら「タスクがありません」が表示される", async ({
  page,
}) => {
  await addTodo(page, "唯一のTodo");
  await page.getByRole("button", { name: "削除" }).first().click();
  await expect(page.getByText("タスクがありません")).toBeVisible({
    timeout: 5000,
  });
});
