import PageLayout from "../PageLayout";

const Loading = () => {
  return (
    <PageLayout>
      <div className="h-16 w-16 animate-spin rounded-full border-4 border-dashed border-gray-300 dark:border-violet-400"></div>
    </PageLayout>
  );
};

export default Loading;
