import PageLayout from "../PageLayout";

const Loading = () => {
  return (
    <PageLayout>
      <div className="w-16 h-16 border-4 border-dashed rounded-full animate-spin border-gray-300 dark:border-violet-400"></div>
    </PageLayout>
  );
};

export default Loading;
